import logging
import re


class SensitiveFilter(logging.Filter):
    def filter(self, record):
        for keyword in ["password", "passwordConfirm", "access", "refresh"]:
            if keyword in record.msg:
                record.msg = self.sanitize_dict(record.msg, keyword)
        return True

    @staticmethod
    def sanitize_dict(msg, keyword):
        regex1 = f'"{keyword}":[ ]*"[^"]*"'
        regex2 = f"{keyword}=[^&]+&?"

        msg = re.sub(regex1, f'"{keyword}": "****"', msg)
        msg = re.sub(regex2, f"{keyword}=****&", msg)
        return msg
