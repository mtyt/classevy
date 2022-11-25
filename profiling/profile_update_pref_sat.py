import cProfile
from classevy.klas import StudentGroup, Plan

#  @profile
def main():
    assignment = [1., 1., 1., 0., 0., 0., 1., 1., 1., 0., 0., 0., 0., 0., 1., 1., 1.,
       1., 1., 1., 1., 1., 0., 1., 0., 0., 1.]
    students = StudentGroup('data/students.csv')
    plan = Plan(students, 2, assignment=assignment)
    _ = plan.students


cProfile.run('main()', 'profiled_update_pref_sat')
#main()