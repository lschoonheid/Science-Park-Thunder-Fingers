from ..classes.schedule import Schedule
import copy


# TODO: #14 implement genetic algorithm to combine schedules into children schedules


class GeneticAlgorithm:
    def __init__(self, prototype: Schedule) -> None:
        self.protoype = copy.deepcopy(prototype)
        # self.make_children(prototype)
        pass

    def make_children(self, prototype: Schedule, n: int = 5):
        child = prototype
        children = []
        for i in range(n):
            child = copy.deepcopy(child)
            children.append(child)

        # print("chidlren id's:")
        # for child in children:
        #     print(id(child))

        # for child in children:
        #     print(f"student id's of child {id(child)}")
        #     for student in child.students:
        #         print(id(student))

    def run(self, n_children: int = 5):
        self.make_children(self.protoype, n_children)
