Select a CSV file from your computer and set the number of classes into which the 
students must be divided.
A CSV file can be generated from Excel, Google Sheets or notepad. It needs to have the following format:
- Use ';' to separate fields.
- The first column must be named 'number' and contain the students' numbers (which must be unique)
- The second column must be named 'name' and contain students' names
- The next columns can be called anything, but should contain things like student scores, gender, etc. 
  All data in these columns should be numeric. For example, gender can be represented by 1,0,-1 for M/X/F 
  By default, the algorithm will try to even out the averages in each class for these numbers. So for example if the total student population
  contains 10 girls and 6 boys, this adds up to an average of -10+6 = -4. When divided into 2 classes, a possible solution would be to have
  5 girls and 3 boys in each class. Each class would then have an average gender of -2. Since this is the same for both classes, the 'spread' of the 'mean' of gender
  is 0, which is the optimization target for the algorithm. Similarly, the algorithm can try to even out math scores between classes etc.
- The last 3 columns should be present in the file, but can be left empty.
  - 'not_together': in each field you can list students that should NOT be in the same class as this student. Specify using student numbers, seperated by comma (',') for example: 4,7,1. Note that every student listed here, should also have this student in their list.
  - 'together': see 'not_together' but for students that should be in the same class as this student.
  - 'preferences': student's own preferences. Should be empty or a list of 3 numbers. The algorithm will make sure that at least 1 of these students is in the same class as this student.

For middle columns like gender and scores, the algorithm will optimize the student division so as to minimize the differences (or spread) of the mean of the values. I.e. evenly distribute.
For the last 3 columns, these are seen as hard requirements. When too many are specified, it's possible that there is no solution.