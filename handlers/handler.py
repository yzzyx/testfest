# -*- coding: utf-8 -*-

test_handler_list = []
def register_handler(cls):
    """ @register_handler decorator - used on all test handlers """
    test_handler_list.append(cls())
    return cls

def process_handlers():
    """ loop through all handlers, and if we find one that is applicable,
        execute it and return the results
    """

    for th in test_handler_list:
        if th.is_applicable():
            (rv, output) = th.run_test()
            (total_tests, failed_tests) = th.parse_test(output)

            return (rv, total_tests, failed_tests, output)
    return (-1, -1, -1, "Could not find a suitable handler!")
