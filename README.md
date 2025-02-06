# domprob 🛰️
Inspired by [this blog post](https://martinfowler.com/articles/domain-oriented-observability.html), domprob is a Python package to implement observability domain probes in your projects.

![PyPI - Package Version](https://img.shields.io/pypi/v/domprob.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/domprob)
[![codecov](https://codecov.io/gh/tenyo-app/pydomprob/graph/badge.svg?token=C0BO1ZP0DK)](https://codecov.io/gh/tenyo-app/pydomprob)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[📄 Documentation](https://domprob.readthedocs.io/en/latest/) | [🐍 PyPI](https://pypi.org/project/domprob/)

## Overview

Keep your business logic comprehensible by abstracting the observability code away.

**Turn this (19 lines):**

```python
class Order:
    def checkout(self):
        self.logger.log(f"Attempting to checkout order {self.order}")
        try:
            self.checkout_service.checkout_order(self.order)
        except CheckoutError as e:
            self.logger.error(f"Checkout for order {self.order} failed: {e}")
            self.metrics.increment("checkout-failed", {
                "failed_orders": 1, "customer": 6234654
            })
            return
        self.logger.log(f"Order checkout completed successfully")
        self.metrics.increment("checkout-successful", {
            "successful_orders": 1, 
            "customer": 6234654, 
            "order_number": 2374, 
            "sku": "JH-374-VJHV"
        })
        self.analytics.add(**self.order.to_dict())
```

**→ Into ✨this✨ (9 lines):**

```python
class Order:
    def checkout(self):
        probe.announce(AttemptingCheckoutObservation())
        try:
            self.checkout_service.checkout_order(self.order)
        except CheckoutError as e:
            probe.announce(CheckoutFailedObservation())
            return
        probe.announce(CheckoutSuccessfulObservation())
```

## Installation

Install using uv:

```shell
uv add domprob
```

Using pip:

```shell
pip install domprob
```

Using poetry:

```shell
poetry add domprob
```

## Usage
