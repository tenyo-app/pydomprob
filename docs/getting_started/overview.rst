Overview
========

Inspired by `this blog post <https://martinfowler.com/articles/domain-oriented-observability.html>`_, keep your business logic comprehensible by abstracting the observability code away.

**Turn this (21 lines):**

.. code-block::

    class OrderService:

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
            self.metrics.increment("checkout-successful", {
                "successful_orders": 1,
             })
            self.logger.log(f"Order checkout completed successfully", {
                "successful_orders": 1,
                "customer": 6234654,
                "order_number": 2374,
                "sku": "JH-374-VJHV"
            })

**→ Into ✨this✨ (9 lines):**

.. code-block::

    class Order:

        def checkout(self):
            probe.observe(AttemptingCheckoutObservation())
            try:
                self.checkout_service.checkout_order(self.order)
            except CheckoutError as e:
                probe.observe(CheckoutFailedObservation())
                return
            probe.observe(CheckoutSuccessfulObservation())
