from enum import Enum,EnumMeta

class VehicleTypeMeta(EnumMeta):
    def __new__(cls, name, bases, dct):
        obj = super().__new__(cls, name, bases, dct)
        # print(dct)
        # print(list(obj.__members__.values())[0].value)
        # # obj._init(dct)\
        # for mname,member in obj.__members__.items():
        #
        #     for tup_ix,prop_name in enumerate(['csv_name','hours','cost']):
        #         setattr(member,prop_name,property(
        #             lambda self, v=None: self.value[tup_ix]
        #         ))
        return obj
class VehiculeCategory(Enum,metaclass=VehicleTypeMeta):
    COMPACT_CAR = ("compact",0.5,150)
    MEDIUM_CAR = ("medium",0.5,150)
    FULLSIZE_CAR = ("full-size",0.5,150)
    CLASS1_TRUCK = ("class 1 truck",1.0,250)
    CLASS2_TRUCK = ("class 2 truck",2.0,700)
    @property
    def csv_name(self):
        return self.value[0]

    @property
    def hours(self):
        return self.value[1]

    @property
    def cost(self):
        return self.value[2]
