#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT

from __future__ import annotations

import time
from typing import Literal

import pytest
from tenacity import RetryError

from teselagen.utils.utils import wait_for_status


class TestUtils:

    def test_wait_for_status(self):
        """Tests wait_for_status happy and sad (timeout) paths with a dummy request."""
        fixed_wait_time = 0.2
        counter_limit = 5

        def validation_method(x: str) -> bool:
            return x == "OK"

        def a_status_request(count_limit: int) -> Literal['OK', 'NOT OK']:
            time.sleep(0.2)
            out = "NOT OK"
            nonlocal counter
            counter += 1
            if counter >= count_limit:
                out = "OK"
            return out

        # Happy path
        counter = 0
        result = wait_for_status(
            method=a_status_request,
            validate=validation_method,
            fixed_wait_time=fixed_wait_time,
            timeout=5,  # timeout >= (fixed_wait_time + request_time) * count_limit = (0.2 + 0.2) * 5 = 2.0
            count_limit=counter_limit,
        )
        assert result == "OK"

        # Timeout fail (timeout argument is reduced)
        counter = 0
        with pytest.raises(RetryError):  # checks exception is raised
            result = wait_for_status(
                method=a_status_request,
                validate=validation_method,
                fixed_wait_time=fixed_wait_time,
                timeout=1,
                count_limit=counter_limit,
            )
