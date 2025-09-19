CREATE TABLE students(
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL
);

INSERT INTO students (name, age)
VALUES ('John Doe', 20), ('Jane Doe', 22);