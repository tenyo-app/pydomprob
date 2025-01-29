# domprob 🛰️
Inspired by [this blog post](https://martinfowler.com/articles/domain-oriented-observability.html), domprob is designed
to be a Python package to implement observability domain probes. View the documentation
[here](https://domprob.readthedocs.io/en/latest/).

## Overview

Keep your business logic tidy and abstract the observability code away.

Change this:

```python
class Order:
    def checkout(self):
        self.logger.log(f"Attempting to checkout order {self.order}")
        try:
            self.checkout_service.checkout_order(self.order)
            return
        except CheckoutError as e:
            self.logger.error(f"Checkout for order {self.order} failed: {e}")
            self.metrics.increment('checkout-failed', ('failed_orders': 1))
        self.logger.log(f"Order checkout completed successfully")
        self.metrics.increment('checkout-successful', ('successful_orders': 1))
```

Into this:

```python
class Order:
    def checkout(self):
        probe.announce(AttemptingCheckoutObservation())
        try:
            self.checkout_service.checkout_order(self.order)
            return
        except CheckoutError as e:
            probe.announce(CheckoutFailedObservation())
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
