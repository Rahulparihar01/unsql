db = db.getSiblingDB('student_master');
db.createCollection('students');

db.students.insert([
    {
        name: 'John Doe',
        age: 20
    },
    {
        name: 'Jane Doe',
        age: 22
    }
]);