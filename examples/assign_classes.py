from classevy.klas import StudentGroup, PlanPopulation


def main(n_gen=10):
    # First create a StudentGroup object from a CSV file:
    students = StudentGroup('data/students.csv')

    # Then assign these students to 20 instances of a Plan with 2 classes:
    # (a Plan is a particular arrangement of all students in the Plan.students
    # into n_classes classes - 2 in this case.)

    # Now create a Population from these plans. A population is the set of plans
    # that we will start from in the genetic algorithm.
    # Also specify the goals and any conditions. In this case, the goals are single
    # values per goal per plan, defined as the standard deviation of the mean values
    # for each class of a particular property of a student.
    # As a single condition, we look at 'assignment_check', which verifies that the
    # 'together', 'not_together' and 'preferences' are fulfilled for each student.
    pop = PlanPopulation(students, 20, 2, goals_dict={
                                        'spread_gender': 'min',
                                        'spread_score_math': 'min',
                                        'spread_score_spelling': 'min',
                                        'spread_size': 'min'
                                    },
                         conditions=['assignment_check']
                         )

    # We can print a few rows of the pop.df:
    print('The first 4 rows of the Population:')
    print(pop.df[0:4])
    print('Each Individual is a Plan object. The spread_ columns are defined as'
          ' the standard deviation across classes of the mean value per class for'
          ' the respective student properties for which we want to optimize a'
          ' balanced division.')

    # Even without running optimization, we can already compute the Pareto front
    # of the current population:
    print(pop.pareto()[pop.goals_dict.keys()])

    print('The Population.summary() contains the mean values for all the goals'
          ' over the population:')
    print(pop.summary())

    pop.run(n_gen)
    pop.plot_progress()

    # The thing with Pareto fronts is that it's impossible to say which solution
    # is the best. For this case, we can say that the sum of the criteria can be
    # minimized:
    front = pop.pareto()
    front['sum'] = sum([front[col] for col in pop.goals_names])
    best_plan = front.sort_values('sum').iloc[0].values[0]

    # We've defined attributes on Plan to represent the values of the average
    # properties in the class:
    print('\nThe best Plan looks like this:\n')
    for prop in pop.goals_names:
        attr_base = prop.replace('spread_', '')
        attr_cl = getattr(best_plan, 'classes_' + attr_base)
        attr_sp = getattr(best_plan, prop)
        print(f'The mean {attr_base} for each class is: {attr_cl}')
        print(f'The spread is: {attr_sp}')

    print('\nThe resulting DataFrame (the final_assignment column counts):')
    print(best_plan.students)


if __name__ == '__main__':
    main(n_gen=10)
