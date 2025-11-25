from abc import ABC, abstractmethod


class IReportService(ABC):

    @abstractmethod
    def create_report(self, ):
        pass

    @abstractmethod
    def delete_report(self, ):
        pass

    @abstractmethod
    def update_report(self, ):
        pass

    @abstractmethod
    def get_report_by_id(self, ):
        pass

    @abstractmethod
    def get_all_reports(self, ):
        pass
