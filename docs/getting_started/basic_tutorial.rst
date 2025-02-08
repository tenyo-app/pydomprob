Basic Tutorial
==============

Defining an 'instrument'
------------------------

Any object can be used as an 'instrument'. Including objects from other libraries and custom objects.

.. code-block:: python
   :linenos:

   import requests


   class MetricsAdapter:

       def __init__(self, uri: str) -> None:
           self.uri = uri

       def increment(self, metric_name: str, increment_amount: int = 1) -> None:
           requests.post(self.uri, {
               "metric_name": metric_name,
               "action": {
                   "type": "increment",
                   "amount": increment_amount
               }
           })


Defining an observation
-----------------------

The best way to define an observation is by creating a class that inherits from
:py:class:`~domprob.observations.base.BaseObservation`. Strictly, any class that implements the
:py:class:`~domprob.observations.observation.ObservationProtocol` is supported, however this isn't recommended.

:py:func:`~domprob.announcements.decorators.announcement` decorators can also be stacked. See the component docs for
more details.

.. note:: When the :py:attr:`required` parameter in an :py:func:`~domprob.announcements.decorators.announcement`
   decorator is set to :py:attr:`True`, an exception will be raised upon no implementation of the same instrument type
   existing in the probe used to make observations. :py:attr:`required` parameter is set to :py:attr:`False` by default.

.. code-block:: python
   :linenos:

   import logging

   from domprob import announcement, BaseObservation


   class CheckoutSuccessful(BaseObservation):

       def __init__(self, **order_details: Any) -> None:
           self.order_details = order_details

       @announcement(logging.Logger, required=True)
       def log_observation(self, log: logging.Logger) -> None:
           log.info("Checkout successful!", **self.order_details)

       @announcement(MetricsAdapter)
       def increment_metric(self, metric_app: MetricsAdapter) -> None:
           metric_app.increment('successful-checkouts', 1)


Calling an observation
----------------------

**With the default probe:**

The default :py:attr:`~domprob.probes.probe.probe` has a single, default logger instance available. This allows you to
start using the library easily; configuring a custom probe is recommended before use in production systems.

.. code-block:: python
   :linenos:
   :emphasize-lines: 1, 10

   from domprob import probe

   class OrderService:

       def checkout(self):
           try:
               self.checkout_service.checkout_order(self.order)
           except CheckoutError as e:
               raise
           probe.observe(CheckoutSuccessfulObservation())


**With a custom probe:**

Configuring a custom probe with user-defined instruments is easy with :py:func:`~domprob.probes.probe.get_probe`. For
more control over customisation, any user-defined class that implements
:py:class:`~domprob.dispatchers.dispatcher.DispatcherProtocol` can be directly passed into the
:py:class:`~domprob.probes.probe.Probe`.

.. code-block:: python
   :linenos:
   :emphasize-lines: 1, 6, 13

   from domprob import get_probe

   class OrderService:

       def __init__(self):
           self.probe = get_probe(logging.getLogger(), MetricsAdapter("<api_endpoint>"))

       def checkout(self):
           try:
               self.checkout_service.checkout_order(self.order)
           except CheckoutError as e:
               raise
           self.probe.observe(CheckoutSuccessful(**self.order_aggregate))
