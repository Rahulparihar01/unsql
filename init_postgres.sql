CREATE TABLE students(
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER NOT NULL
);

INSERT INTO students (name, age)
VALUES ('John Doe', 20), ('Jane Doe', 22);