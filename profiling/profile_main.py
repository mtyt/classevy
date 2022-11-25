import cProfile
from assign_classes import main


cProfile.run('main()', 'profiled')
