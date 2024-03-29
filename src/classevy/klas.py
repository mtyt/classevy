"""Module for creating classes with students, and plans which assign students
to classes."""
from functools import partial
import ast
import os
from typing import Optional, Union, List, Tuple
from copy import deepcopy
import numpy as np
import pandas as pd
from optime.ga import Population
from .helpers import next_best, divide_list, Numeric, divide_num


rng = np.random.default_rng()


class StudentGroup(pd.DataFrame):
    """Any list of Students. We can do some basic calculations on this list.
    TODO: Currently, df is not automatically updated. This can cause issues if
    we add students after init.
    """

    _metadata = [
        "required_columns"
    ]  # avoid UserWarning: Pandas doesn't allow columns to be created via a new
    # attribute name

    @classmethod
    def read_file(cls, path: str) -> pd.DataFrame:
        """Correctly parse an Excel or CSV file and return a dataframe."""

        def read_tuple(x: Union[str, Numeric]) -> tuple:
            if x == "":
                x_n = ()
            else:
                if not isinstance(x, str):
                    try:
                        x = str(x)
                    except Exception:
                        raise ValueError("can't make x string")
                x_n = ast.literal_eval(x)
                if not isinstance(x_n, tuple):
                    return tuple([x_n])
            return x_n

        # Determine the file type
        extension = os.path.splitext(path)[-1]
        excel_extensions = [".xlsx", "xls"]
        csv_extensions = [".csv", ""]
        if extension in excel_extensions:
            filetype = "excel"
        elif extension in csv_extensions:
            filetype = "csv"
        else:
            raise ValueError(
                f"Filetype with extension {extension} not supported."
                + "Valid extensions are "
                + ", ".join(excel_extensions + csv_extensions)
                + ". Files without extensions are assumed to be CSV."
            )

        conv = {
            "not_together": read_tuple,
            "together": read_tuple,
            "preferences": read_tuple,
        }
        df: pd.DataFrame
        if filetype == "csv":
            df = pd.read_csv(
                path,
                delimiter=";",
                converters=conv,
            )
        elif filetype == "excel":
            df = pd.read_excel(path, converters=conv)
        else:
            raise ValueError("No other extensions supported.")

        df = df.set_index("number", verify_integrity=True)

        # Now perform some checks on the data.
        # The columns, not_together, together, preferences and  name should
        # be present
        if "name" not in df.columns:
            raise ValueError('No column "name" found.')
        if "not_together" not in df.columns:
            raise ValueError('No column "not_together" found.')
        if "together" not in df.columns:
            raise ValueError('No column "together" found.')
        if "preferences" not in df.columns:
            raise ValueError('No column "preferences" found.')

        # each together and not_together entry should be reciprocal
        for number, row in df.iterrows():
            for col in ["not_together", "together"]:
                for other in row[col]:
                    other_student = df.loc[other]
                    if number not in other_student[col]:
                        raise ValueError(
                            f"Student with number {number} is"
                            f" not in Student with number {other} {col} list"
                            f" but {other} is in {number}"
                        )

        # the preferences should be tuples with 0 or 3 numbers and not contain
        # the student's own
        for i, row in df.iterrows():
            tup = row["preferences"]
            if not isinstance(tup, tuple):
                raise TypeError(
                    f"Expected a tuple but got {type(tup)}. Is"
                    " the 'preferences' column correctly formatted?"
                )
            if not ((len(tup) == 3) or (len(tup) == 0)):
                raise ValueError(
                    "The 'preferences' should contain 3"
                    f" values but has {len(tup)} for student with number"
                    f"{i}."
                )
            if len(tup) == 0:
                # set the value to the student number so it's always satisfied.
                df.loc[i, "preferences"] = (i,)

        # All numbers in not_together, together and preferences columns should
        # be inside the student numbers.
        all_numbers = df.index.values
        cols = ["not_together", "together", "preferences"]
        for col in cols:
            for tup in df[col]:
                if len(tup):
                    check = all([num in all_numbers for num in tup])
                    if not check:
                        raise ValueError(
                            f"In {col}, there's a value that's" " not a student number"
                        )
        return df

    def __init__(self, data: Optional[Union[pd.DataFrame, str]]) -> None:
        required_columns: List[str] = [
            "name",
            "together",
            "not_together",
            "preferences",
        ]
        all_columns = ["number"] + required_columns
        if data is None:
            data = pd.DataFrame(columns=all_columns)
        if isinstance(data, pd.DataFrame):
            super().__init__(data)
        elif isinstance(data, str):
            df_students = StudentGroup.read_file(data)
            super().__init__(df_students)
        else:
            raise TypeError(
                "Input to StudentGroup should be DataFrame or str (path to CSV file"
            )
        self.required_columns = required_columns

    @property
    def size(self) -> int:
        """Size is len."""
        return len(self)

    @property
    def properties(self) -> List[str]:
        """returns a list of column names that are not required_columns."""
        return [col for col in self.columns if col not in self.required_columns]

    def divide_one_prop(
        self, prop: str, n_classes: int
    ) -> Tuple[List[List[Numeric]], List[Numeric], Numeric]:
        """Perform a so-called Partition problem algorithm on the property 'prop' of
        the plan. Assign each number in the descending-ordered list of the property to
        the class for which the spread would increase the least. This is regardless of
        all the other properties: what is the best spread we could obtain for this prop.
        The method returns the classes (lists of the prop), the mean for each class,
        and the standard deviation of those means across the classes.

        Args:
            prop: Represents the property to be divided over classes
            n_classes: number of classes over which to divide

        Returns:
            classes, means, spread
        """

        return divide_list(list(self[prop].values), n_classes)


class Klas:
    """Class for a Klas, which is a class as in it has students. It has a
    StudentGroup but a Studentgroup doesn't always have to be a Klas.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        students: Optional[Union[str, pd.DataFrame, StudentGroup]] = None,
        conditions: Optional[List[str]] = None,
    ) -> None:
        self.name = name
        if students is None:
            students = StudentGroup(None)
        elif isinstance(students, str):
            students = StudentGroup(students)
        elif isinstance(students, StudentGroup):
            pass  # just pre-empt next elif
        elif isinstance(students, pd.DataFrame):
            students = StudentGroup(students)
        else:
            raise TypeError(
                "students argument must be StudentGroup, None, str or DataFrame"
            )
        self.students = students
        if conditions is None:
            conditions = []
        self.conditions = conditions

    def print_names(self) -> None:
        """Print all the names."""
        for name in self.students["name"]:
            print(name)

    @property
    def size(self) -> int:
        """return the length of the class.students."""
        return len(self.students)


class NoSolutionError(Exception):
    pass


class Plan:
    """A Plan is a particular assignment of students over classes. It can be
    evaluated based on some criteria.
    """

    def __init__(
        self,
        students: StudentGroup,
        n_classes: int = 2,
        assignment: Optional[List[int]] = None,
    ):
        if not isinstance(students, StudentGroup):
            raise TypeError("students should be a StudentGroup")
        self.students = StudentGroup(deepcopy(students))
        self.n_classes = n_classes
        if assignment is None:
            self.assignment_fixed = (
                False  # Allow algo to retry with different assignment
            )
            assignment = list(rng.integers(0, n_classes, len(students)))
        else:
            self.assignment_fixed = True
        self.assignment = assignment  # use setter

    @property
    def assignment(self) -> List[int]:
        """returns self._assignment."""
        return self._assignment

    @assignment.setter
    def assignment(self, val: List[int]) -> None:
        """Set the assignment and immediately calculate the final assignment."""
        self._assignment = val
        self.init_students_df()
        try:
            self.do_assignment()
        except NoSolutionError:
            if not self.assignment_fixed:
                assignment = list(rng.integers(0, self.n_classes, len(self.students)))
                self.assignment = assignment  # making it recursive
            else:
                raise NoSolutionError(
                    "Assignment is fixed, algo currently at dead end."
                )
        self.improve_preferences()

    def spreadprops(self, prop: str) -> float:
        """Returns the standard dev of the mean value of the propery of all
        the classes.
        """
        return np.array(self.allprops(prop)).std()

    def allprops(self, prop: str) -> List[Union[int, float]]:
        """Returns a list of the mean of property for each class in the list.
        In case of prop='size', return the size of each class.
        """
        if prop == "size":
            return [klas.size for klas in self.classes]
        else:
            return [klas.students[prop].mean() for klas in self.classes]

    @property
    def students(self) -> StudentGroup:
        """standard getter"""
        return self._students

    @students.setter
    def students(self, student_group: StudentGroup) -> None:
        # Set property for all StudentGroup.properties:
        # spread_prop for the standard deviation across the mean value of the
        # prop per class.
        if not isinstance(student_group, StudentGroup):
            raise TypeError(
                "Value must be a StudentGroup," f" but is {type(student_group)}"
            )
        for prop in student_group.properties + ["size"]:
            fget_spread = partial(self.__class__.spreadprops, prop=prop)
            setattr(self.__class__, "spread_" + prop, property(fget=fget_spread))
            fget_all = partial(self.__class__.allprops, prop=prop)
            setattr(self.__class__, "classes_" + prop, property(fget=fget_all))
        self._students = student_group

    def init_students_df(self) -> None:
        """Initialize the students with some additional columns."""
        self.students["options"] = [
            list(range(self.n_classes)) for _ in range(len(self.students))
        ]
        self.students["dna_assignment"] = self.assignment
        self.students["final_assignment"] = np.zeros(len(self.students))
        self.students["pref_satisfied"] = np.zeros(len(self.students))
        # add these here so they don't show up in students.properties:
        self.students.required_columns = self.students.required_columns + [
            col
            for col in [
                "options",
                "dna_assignment",
                "final_assignment",
                "pref_satisfied",
            ]
            if col not in self.students.required_columns
        ]

    @staticmethod
    def update_pref_sat(df: pd.DataFrame, i: int) -> None:
        """Update the pref_satistfied column for student with number i"""
        curr_finass = df.at[i, "final_assignment"]
        curr_pref = list(df.at[i, "preferences"])
        # limit the preferences to check to those in df.index:
        curr_pref = [pref for pref in curr_pref if pref in df.index]
        pref_sat = 0
        for pref in curr_pref:
            if df.at[pref, "final_assignment"] == curr_finass:
                pref_sat += 1
        df.at[i, "pref_satisfied"] = pref_sat

    @staticmethod
    def update_all_pref_sat(df: pd.DataFrame) -> None:
        """Update the pref_satisfied column for all students."""
        for i in df.index.values:
            Plan.update_pref_sat(df, i)

    def do_assignment(self, flag_prio_prefs: bool = False, verbose: bool = False):
        """Based on:
            - self.assignment (DNA)
            - student's preferences
            - together and not_together columns
        try to find an assignmenet of students into classes that satisfies the
        preferences and together and not_together requirements. DNA takes a
        second place.
        """
        self.init_students_df()
        # script flags:
        # flag_prio_prefs: prioritize preferences over DNA
        students = self.students
        for i in students.index.values:
            student: pd.Series = students.loc[i]
            curr_options: List[int] = student["options"]
            curr_dna: int = student["dna_assignment"]
            dna_in_options: bool = curr_dna in curr_options
            curr_pref: Tuple[int] = student["preferences"]
            if verbose:
                print("\n----------")
                print(i, student["name"])
                print("Options:", curr_options)
                print("DNA:", curr_dna)
                print("DNA is in options:", dna_in_options)
                print("Preferences:", curr_pref)

            final_assignment: int
            if flag_prio_prefs:
                # first choose a final_assignment based on
                # 1. look at previous students in the current student's
                # preferences.
                prev_in_pref: List[int] = [pref for pref in curr_pref if pref < i]
                if verbose:
                    print("Previous students in preferences:", prev_in_pref)
                df_pref: pd.DataFrame = students.loc[prev_in_pref]
                # now filter by those that have their final_assignment in
                # curr_options
                df_pref = df_pref[df_pref["final_assignment"].isin(curr_options)]
                if len(df_pref) > 0:
                    if verbose:
                        print("Found valid previous students that are in preferences")
                    # check if any have i in their preferences &
                    # not pref_satisfied
                    msk_1 = df_pref["options"].apply(lambda x, val=i: val in x)
                    msk_2 = df_pref["pref_satisfied"].apply(lambda x: x == 0)
                    df_pref_prio = df_pref[msk_1 & msk_2]
                    if not len(df_pref_prio) > 0:  # we found preferred previous
                        # students, but not extra preferences satisfied:
                        df_pref_prio = df_pref
                else:
                    if verbose:
                        print(
                            "no valid previous students are found that are"
                            " in the preferences."
                        )
                    # so go check if any previous students have i in their
                    # preferences and not pref_satisfied
                    df_pref = students.loc[: i - 1]
                    df_pref = df_pref[df_pref["final_assignment"].isin(curr_options)]
                    # check if any have i in their preferences
                    # & not pref_satisfied
                    msk_1 = df_pref["preferences"].apply(lambda x, v=i: v in x)
                    msk_2 = df_pref["pref_satisfied"].apply(lambda x: x == 0)
                    df_pref_prio = df_pref[msk_1 & msk_2]
                    if len(df_pref_prio) > 0:
                        if verbose:
                            print(
                                "But previous students have this student in"
                                " their preferences and they do not have"
                                " pref_satisfied"
                            )
                    # if that is not the case, no preferences can be satisfied,
                    # and we should just pick a class based on options and dna.

                # check again if there are any options left:
                if len(df_pref_prio) > 0:
                    if verbose:
                        print(
                            "df_pref_prio:",
                            df_pref_prio[
                                ["name", "final_assignment", "pref_satisfied"]
                            ],
                        )
                    # first see of any of them match with the dna, otherwise,
                    # pick the first one:
                    if curr_dna in df_pref_prio["final_assignment"].values:
                        if verbose:
                            print("Found DNA in previous preferred students")
                        final_assignment = curr_dna
                    else:
                        if verbose:
                            print(
                                "Did not find DNA in previous preferred"
                                " students so will take first one"
                            )
                        final_assignment = df_pref_prio.iloc[0]["final_assignment"]
                else:
                    # just pick DNA if it's in the options and if not, the next
                    # item in options (go around)
                    final_assignment = next_best(student["options"], curr_dna)
            else:
                if verbose:
                    print("Ignoring preferences, just trying DNA if it's in options")
                # just pick DNA if it's in the options and if not, the next item
                # in options (go around)
                final_assignment = next_best(student["options"], curr_dna)
            # now the current student has a final_assignment.
            if verbose:
                print("Final assignment:", final_assignment)
            students.at[i, "final_assignment"] = int(final_assignment)
            # verify if any of the previous students now have their
            # pref_satisfied.
            self.update_all_pref_sat(students.loc[:i])

            # now update the options column of next students:
            # if current student has_not_tog:
            # remove current_student[final_assignment] from those student's
            # options
            # if current student has_tog:
            # only keep current_student[final_assignment] in those
            # student's options.

            has_not_tog = len(student["not_together"]) > 0
            if has_not_tog and verbose:
                print("Not_together:", student["not_together"])
            for not_tog in student["not_together"]:
                if final_assignment in students.at[not_tog, "options"]:
                    if verbose:
                        print(
                            f"removing option {final_assignment} from"
                            f" student {not_tog}:"
                            f' {students.at[not_tog, "name"]}'
                        )
                    students.at[not_tog, "options"].remove(final_assignment)
                    if not len(students.at[not_tog, "options"]):
                        raise NoSolutionError(
                            "The current combination of student data"
                            + " and assignment yields no valid solution."
                        )
            has_tog = len(student["together"]) > 0
            if has_tog and verbose:
                print("together:", student["together"])
            for tog in student["together"]:
                if verbose:
                    print(
                        f"setting options for student {tog}:"
                        f' {students.at[tog, "name"]} to {final_assignment}'
                    )
                students.at[tog, "options"] = [final_assignment]

    @staticmethod
    def update_class_to_improve_pref(df: pd.DataFrame, i: int, verbose=False):
        """Go through the student's options to see if we can change its class
        in order to improve its pref_satisfied to be >0.
        """
        original_assignment: int = df.at[i, "final_assignment"]
        other_options: List[int] = [
            j for j in df.at[i, "options"] if not j == original_assignment
        ]
        for option in other_options + [original_assignment]:  # if other options
            # don't improve things, go back to original
            new_assignment: int = option
            df.at[i, "final_assignment"] = int(new_assignment)
            Plan.update_pref_sat(df, i)
            if df.at[i, "pref_satisfied"] > 1:  # break loop as soon as it's ok
                if verbose:
                    print(
                        f'Updating student {i}: {df.at[i, "name"]} from'
                        f" {original_assignment} to {new_assignment}"
                    )
                    print("Now the pref_sat is: ", df.at[i, "pref_satisfied"])
                break

    @staticmethod
    def update_other_students_to_improve_pref(df: pd.DataFrame, i: int, verbose=False):
        """Go through the student's preferences and see if you can change one
        of their classes in order to improve this student's pref_satisfied.
        The condition for making a change is that the total number of
        pref_satisfied>0 increases.
        """
        count_pref_sat: int = sum(df["pref_satisfied"] > 0)
        preferences: Tuple[int] = df.at[i, "preferences"]
        # can I change one of the prefered student's classes without making
        # their pref_satisfied 0?
        for k in preferences:
            original_assignment: int = df.at[k, "final_assignment"]
            other_options: List[int] = [
                j for j in df.at[k, "options"] if not j == original_assignment
            ]
            for option in other_options + [original_assignment]:  # if other
                # options don't improve things, go back to original
                new_assignment: int = option
                df.at[k, "final_assignment"] = int(new_assignment)
                Plan.update_all_pref_sat(df)
                new_count_pref_sat: int = sum(df["pref_satisfied"] > 0)
                if new_count_pref_sat > count_pref_sat:
                    if verbose:
                        print(
                            f'Updating student {k}: {df.at[k, "name"]}'
                            f" from {original_assignment} to {new_assignment}"
                        )
                        print(
                            "The number of preferences satisfied went from"
                            f" {count_pref_sat} to {new_count_pref_sat}."
                        )
                    break

    def improve_preferences(self, max_tries: int = 10, verbose: bool = False) -> None:
        """Check the pref_satisfied of all the students. If not all of them are
        >0, try to improve things by applying the methods
        update_class_to_improve_pref and update_other_students_to_improve_pref
        on each student with pref_satisfied == 0. Keep trying this across all
        students until all are >0 or for a maximum number of times.
        """
        trying: int = 0
        students: StudentGroup = self.students
        count_pref_sat: int = sum(students["pref_satisfied"] > 0)
        all_pref_sat: bool = count_pref_sat == len(students)
        while (not all_pref_sat) and trying < max_tries:
            trying += 1
            if verbose:
                print("Try:", trying)
            for i in students.index.values:
                if not students.at[i, "pref_satisfied"]:
                    if verbose:
                        print(f'Working on {i}: {students.at[i, "name"]}')
                    self.update_class_to_improve_pref(students, i, verbose)
                    self.update_all_pref_sat(students)
                    previous_count: int = count_pref_sat
                    count_pref_sat = sum(students["pref_satisfied"] > 0)
                    all_pref_sat = count_pref_sat == len(students)
                    if verbose:
                        print(
                            "Number of students with at least 1 preference"
                            " satisfied = ",
                            count_pref_sat,
                        )
                    # if the count didn't go up, try swapping the student's
                    # prefered students.
                    if not count_pref_sat > previous_count:
                        if verbose:
                            print("Trying preferred students.")
                        self.update_other_students_to_improve_pref(students, i, verbose)
                    previous_count = count_pref_sat
                    count_pref_sat = sum(students["pref_satisfied"] > 0)
                    all_pref_sat = count_pref_sat == len(students)

    def check_assignment(self, raise_exception: bool = False) -> bool:
        """Check if all together and not_together as well as preferences are
        satisfied.
        """
        check: bool = True
        # check that the not_together and together conditions are satisfied:
        for i, stu in self.students.iterrows():
            for not_tog in stu["not_together"]:
                check = (
                    self.students.at[not_tog, "final_assignment"]
                    != stu["final_assignment"]
                )
                if not check:
                    if raise_exception:
                        raise ValueError(
                            f"Students {i} and {not_tog}"
                            " are together and should not!"
                        )
                    break

            for tog in stu["together"]:
                check = (
                    self.students.at[tog, "final_assignment"] == stu["final_assignment"]
                )
                if not check:
                    if raise_exception:
                        raise ValueError(
                            f"Students {i} and {tog} are not" " together and should be!"
                        )
                    break

        # check that the pref_satisfied is >0 for all students that have preferences:
        pref_mask = self.students["preferences"].apply(lambda x: len(x) > 0)
        check = sum(self.students["pref_satisfied"] > 0) == len(
            self.students.loc[pref_mask]
        )

        return check

    @property
    def final_assignment(self) -> List[int]:
        """After assignment algo, return assignments."""
        return self.students["final_assignment"].values

    @property
    def assignment_check(self) -> bool:
        """Returns self.check_assignment() as an attribute."""
        return self.check_assignment()

    @property
    def classes(self) -> List[Klas]:
        """Return the classes of the Plan, with all the students assigned to
        them.
        """
        class_list: list = list(range(int(max(self.final_assignment) + 1)))
        classes: list = []
        for i in class_list:
            students = StudentGroup(
                self.students[self.students["final_assignment"] == i]
            )
            students.required_columns = (
                self.students.required_columns
            )  # to fix properties
            classes.append(Klas(name=f"Class_{i}", students=students))
        return classes

    def print_classes(self) -> None:
        """Print the name of each class and the students in it."""
        for klas in self.classes:
            print(
                f"Klas heet {klas.name} en bevat studenten:"
                f'{[name for name in klas.students["name"]]}'
            )

    @property
    def min_class_size(self) -> int:
        """Returns the minimum size of the classes."""
        return min(self.classes_size)  # type: ignore[attr-defined]

    @property
    def max_class_size(self) -> int:
        """Returns the maximum size of the classes."""
        return max(self.classes_size)  # type: ignore[attr-defined]

    @property
    def summary(self) -> dict:
        """Returns a dict with all the classes_prop and spread_prop."""
        summary_dict = {}
        for prop in self.students.properties + ["size"]:
            summary_dict["classes_" + prop] = getattr(self, "classes_" + prop)
            summary_dict["spread_" + prop] = getattr(self, "spread_" + prop)
        return summary_dict

    def print_summary(self) -> None:
        """Print the summary."""
        for prop, val in self.summary.items():
            if "classes" in prop:
                print("Mean", prop, "per class:", val)
            elif "spread" in prop:
                print("Spread of mean", prop, "over classes:", val)

    @property
    def df_summary(self) -> pd.DataFrame:
        """Returns a dataframe representation of the summary"""
        df = pd.DataFrame(
            columns=self.students.properties,
            index=["mean in class" + str(i) for i in range(self.n_classes)]
            + ["spread"],
        )
        for prop in df.columns:

            for i in range(self.n_classes):
                df.at["mean in class" + str(i), prop] = getattr(
                    self, "classes_" + prop
                )[i]
                df.at["spread", prop] = getattr(self, "spread_" + prop)
        return df

    @property
    def classes_df_output(self) -> List[pd.DataFrame]:
        """Returns a list of dataframes, one for each class, with some temporary
        columns dropped.
        """
        return [
            k.students.drop(columns=["options", "dna_assignment", "final_assignment"])
            for k in self.classes
        ]

    @property
    def df_means_classes(self) -> List[pd.DataFrame]:
        """Returns a list of dataframes, one for each class, with the averages of each
        property in students.properties."""
        df_means_list = []
        for stu in self.classes_df_output:
            df_means = pd.DataFrame(columns=stu.columns, index=["Average"])
            for col in self.classes[0].students.properties:
                mean = stu[col].mean()
                df_means.iloc[0][col] = mean
            df_means_list.append(df_means)
        return df_means_list

    def write_excel(self, filename):
        """Write the plan to an Excel file. First page contains all students, next
        pages show each class + average values for properties."""
        plan_output = self.students.drop(columns=["options", "dna_assignment"])
        if os.path.exists(filename):
            os.remove(filename)
        with pd.ExcelWriter(filename, engine="openpyxl") as writer:
            # All the students on first sheet:
            plan_output.to_excel(writer, sheet_name="All Students")
            # 1 sheet per class
            for i, stu in enumerate(self.classes_df_output):
                stu.to_excel(writer, sheet_name=f"Klas {self.classes[i].name}")

        startrow = max([len(stu) for stu in self.classes_df_output]) + 2
        with pd.ExcelWriter(
            filename, engine="openpyxl", mode="a", if_sheet_exists="overlay"
        ) as writer:
            # append averages below students in each class:
            for i, klas in enumerate(self.classes):
                self.df_means_classes[i].to_excel(
                    writer,
                    sheet_name=f"Klas {klas.name}",
                    startrow=startrow,
                    header=False,
                )


class PlanPopulation(Population):
    """Inherits from optime's Population but tailored for Plan."""

    def __init__(
        self,
        students: StudentGroup,
        n_pop: int,
        n_classes: int,
        goals_dict: Optional[dict] = None,
        conditions: Optional[list] = None,
    ):
        if not isinstance(students, StudentGroup):
            raise TypeError("students should be a StudentGroup")
        # set population.students so it can be used to obtain the goals_dict
        self.students = students
        self.n_classes = n_classes
        self.n_pop = n_pop
        if goals_dict is None:
            goals_dict = self.default_goals_dict
        if conditions is None:
            conditions = ["assignment_check"]

        class PlanGA(Plan):
            def __init__(self, *args, **kwargs) -> None:
                super().__init__(*args, **kwargs)

            dna = Plan.assignment
            parent_props = ["students", "n_classes"]
            
            def __repr__(self):
                return f"Plan({self.n_classes} classes, {len(self.students)} students)"

        plans = [PlanGA(students, n_classes) for _ in np.arange(n_pop)]
        super().__init__(plans, goals_dict, conditions)

    def __repr__(self):
        return f"PlanPopulation({self.n_pop} Plans, {self.n_classes} classes)"

    @property
    def default_goals_dict(self):
        # take all the spread_prop of all prop in students.properties, target = 'min'
        # and also size!
        df_targets = self.df_all_students_goals_limits
        default_goals = {}
        for prop in df_targets.columns:
            goal_name = "spread_" + prop
            goal_direction = "min"
            goal_target = df_targets.at["spread", prop]
            default_goals[goal_name] = {
                "direction": goal_direction,
                "target": goal_target,
            }

        return default_goals

    @property
    def df_all_students_goals_limits(self) -> pd.DataFrame:
        """Returns a dataframe containing the best possible limits for all of the
        properties if they have a goal in the goals_dict.
        """
        df = pd.DataFrame(
            columns=self.students.properties + ["size"],
            index=["mean in class" + str(i) for i in range(self.n_classes)]
            + ["spread"],
        )
        for prop in df.columns:
            means: List[Numeric]
            if prop == "size":
                means = divide_num(len(self.students), self.n_classes)
                spread = np.array(means).std()
            else:
                classes, means, spread = self.students.divide_one_prop(
                    prop, self.n_classes
                )
            df.at["spread", prop] = spread
            for i in range(self.n_classes):
                df.at["mean in class" + str(i), prop] = means[i]
        return df
