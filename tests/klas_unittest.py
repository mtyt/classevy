'''Unit tests for the klas.py module'''
import unittest
from os import path
import numpy as np
import pandas as pd
from classevy import klas

rng = np.random.default_rng()

DATA_FOLDER = 'data'

class TestFunctions(unittest.TestCase):
    '''Unit tests for module-level functions.'''
    def test_next_best(self):
        '''Test the next_best function.'''
        options = [0, 1, 2, 4]
        self.assertEqual(klas.next_best(options, 0), 0)
        self.assertEqual(klas.next_best(options, 1), 1)
        self.assertEqual(klas.next_best(options, 2), 2)
        self.assertEqual(klas.next_best(options, 3), 4)
        self.assertEqual(klas.next_best(options, 5), 0)

class TestStudentGroup(unittest.TestCase):
    '''Unit tests for StudentGroup class'''
    def test(self):
        '''Read a list of students from a csv file (try 3 construction methods)
        and test if the properties are constructed correctly.'''
        df_students = klas.StudentGroup.read_csv(path.join(DATA_FOLDER,
                                                           'students.csv'))

        # trigger errors:
        def load_error():
            _ = klas.StudentGroup.read_csv(path.join(DATA_FOLDER,
                                                     'students_wrong.csv'))
        self.assertRaises(ValueError, load_error)

        # 1: start from df:
        students = klas.StudentGroup(df_students)
        self.assertIsInstance(students, klas.StudentGroup)

        # 2: start from string (path)
        students = klas.StudentGroup(path.join(DATA_FOLDER,'students.csv'))
        self.assertIsInstance(students, klas.StudentGroup)
        self.assertEqual(students.size, len(students))

        # 4: force error:
        def yield_error():
            _ = klas.StudentGroup(None)
        self.assertRaises(TypeError, yield_error)


class TestKlas(unittest.TestCase):
    '''Unit tests for Klas'''
    def test_defaults(self):
        '''Instantiate Klas with default arguments'''
        _ = klas.Klas()

    def test_known_students(self):
        '''Create a Klas with 2 known students so we can check calculation of
        some properties.
        '''
        _ = klas.Klas(students=klas.StudentGroup(path.join(DATA_FOLDER,
                                                           'students.csv')))


class TestPlan(unittest.TestCase):
    '''Unit tests for the Plan class.'''
    def test_auto_assign(self):
        '''Test if the auto-assignment works.'''
        for n_classes in range(2,5):
            students = klas.StudentGroup(path.join(DATA_FOLDER,
                                                   'students.csv'))
            p_1 = klas.Plan(students,
                        n_classes,
                        assignment=None
            )
            # check that the assignment is a vector of length of students with
            # numbers ranging from 0 to n_classes-1
            self.assertEqual(len(p_1.assignment), len(p_1.students))
            checks = [i in range(n_classes) for i in p_1.assignment]
            self.assertTrue(all(checks))

            # now check that all the students are in 1 (and only 1) of the
            # classes of the plan the assignment may be correct, but also check
            # the attribute plan.classes:
            stu_in_1_class = []
            for num in p_1.students.index:
                stu_in_1_class.append(sum([num in cl.students.index
                                           for cl in p_1.classes]) == 1)
            self.assertTrue(all(stu_in_1_class))
            p_1.print_classes()

            # now test if the dynamically generated attributes work.
            for prop in p_1.students.properties:
                # the spread properties should be floats:
                self.assertIsInstance(getattr(p_1, 'spread_' + prop), float)
                # the classes properties should be lists:
                self.assertIsInstance(getattr(p_1, 'classes_' + prop), list)
                 #... with length equal to classes:
                self.assertEqual(len(getattr(p_1, 'classes_' + prop)),
                                 len(p_1.classes))

            for prop in ['min_class_size', 'max_class_size']:
                self.assertIsInstance(getattr(p_1, prop), int)

            _ = p_1.summary
            p_1.print_summary()


    def test_do_assignment_improve(self):
        '''Some more tests for functions in class with different conditions.'''
        for stu_file in ['students.csv',
                         'students_short.csv',
                         'students_short_hard.csv',
                         'students_short_impossible.csv']:
            students = klas.StudentGroup(path.join(DATA_FOLDER, stu_file))
            p_1 = klas.Plan(students,
                        2,
                        assignment=None
            )
            p_1.do_assignment(verbose=True)
            p_1.do_assignment(flag_prio_prefs=False, verbose=True)
            p_1.improve_preferences(max_tries=4, verbose=True)
            p_1.do_assignment(flag_prio_prefs=True, verbose=True)
            p_1.improve_preferences(max_tries=4, verbose=True)
            ass_check = p_1.assignment_check
            self.assertIsInstance(ass_check, bool)

class TestPlanPopulation(unittest.TestCase):
    '''Tests for PlanPopulation class.'''
    def test(self):
        '''General test'''
        students = klas.StudentGroup(path.join(DATA_FOLDER,
                                                   'students.csv'))
        goals_dict = {f'spread_{prop}':'min' for prop in students.properties}
        pop = klas.PlanPopulation(students,20, 2, goals_dict=goals_dict,
                                  conditions=['assignment_check'])
        self.assertIsInstance(pop.df, pd.DataFrame)

if __name__ == '__main__':
    unittest.main()
