import numpy as np
import pandas as pd
from classevy import StudentGroup, Klas, Plan
from optime import child, Population
import matplotlib.pyplot as plt

# First create a StudentGroup object from a CSV file:
students = StudentGroup('data/students.csv')

# Then assign these students to 20 instances of a Plan with 2 classes:
# (a Plan is a particular arrangement of all students in the Plan.students
# into n_classes classes - 2 in this case.)
plans = [Plan(students, 2) for _ in np.arange(20)]

# Now create a Population from these plans. A population is the set of plans
# that we will start from in the genetic algorithm.
# Also specify the goals and any conditions. In this case, the goals are single
# values per goal per plan, defined as the standard deviation of the mean values
# for each class of a particular property of a student.
# As a single condition, we look at 'assignment_check', which verifies that the
# 'together', 'not_together' and 'preferences' are fulfilled for each student.
pop = Population(plans, goals_dict={
                                    'spread_gender':'min',
                                    'spread_score_math':'min',
                                    'spread_score_spelling':'min',
                                    'spread_size':'min'
                                   },
                conditions = ['assignment_check'])

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

# Now in order to optimize, we have to define a property on the individual
# class of the population which represents the dna of the individual.
# Currently the implementation is a bit cumbersome for this case, because we 
# have to define getters and setters. Probably this could be done more
# elegantly.
def get_dna(self):
    return self.assignment
def set_dna(self, val):
    setattr(self, 'assignment', val)
    self.init_students_df()
    self.do_assignment()
    self.improve_preferences()

Plan.dna = property(fget = get_dna, fset = set_dna)
Plan.parent_props = ['students', 'n_classes']

n_gen = 10 # number of generations
summaries = []
for gen in np.arange(n_gen):
    pop.make_offspring()
    pop.trim()
    summaries.append(pop.summary())
    
# Then we can plot the progress of the optimization over generations as the
# summary values:
fig, ax = plt.subplots(ncols=1, nrows=len(pop.summary()))
fig.set_size_inches(8,8)
for i,summ in enumerate(pop.summary()):
    y = [gen[summ] for gen in summaries]
    ax[i].plot(y)
    ax[i].set_ylabel(summ)
    
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
