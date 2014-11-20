# -*- coding: utf-8 -*-

test_handler_list = []
def register_handler(cls):
    """ @register_handler decorator - used on all test handlers """
    test_handler_list.append(cls())
    return cls

def process_handlers(branch):
    """ loop through all handlers, and if we find one that is applicable,
        execute it and return the results
    """

    for th in test_handler_list:
        if th.is_applicable():
            return th.run_test(branch)
    return {"total_tests": -1, "failed_tests": -1, "output": "Could not find a suitable handler!"}
