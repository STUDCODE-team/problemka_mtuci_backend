from enum import Enum


class ReportCategory(str, Enum):
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    FURNITURE = "furniture"
    IT_EQUIPMENT = "it_equipment"
    CLEANING = "cleaning"
    HEATING = "heating"
    OTHER = "other"
