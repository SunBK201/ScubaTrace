import scubatrace


def add(a, b):
    return a + b


def main():
    a = 3
    b = 4
    c = add(a, b=b)
    return c


def test_cfg():
    project = scubatrace.PythonProject(".")
    file = project.files["test.py"]
    file.export_cfg_dot("test.dot")


if __name__ == "__main__":
    main()
