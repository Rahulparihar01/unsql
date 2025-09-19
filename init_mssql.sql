USE student_master;
GO

CREATE TABLE Students (
    ID INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL,
    Age INT NOT NULL
);
GO

INSERT INTO Students (Name, Age)
VALUES (N'John Doe', 20), (N'Jane Doe', 22);
GO