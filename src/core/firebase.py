from typing import Dict, List, Optional, Union

from firebase_admin import App, initialize_app, messaging

# cred = credentials.Certificate(google_settings.APPLICATION_CREDENTIALS)
# initialize_app(cred)
initialize_app()


def send_message(
    token: Optional[str] = None,
    data: Optional[Dict[str, str]] = None,
    notification: Optional[messaging.Notification] = None,
    android: Optional[messaging.AndroidConfig] = None,
    webpush: Optional[messaging.WebpushConfig] = None,
    apns: Optional[messaging.APNSConfig] = None,
    fcm_options: Optional[messaging.FCMOptions] = None,
    topic: Optional[Union[str, set]] = None,
    condition: Optional[str] = None,
    dry_run: Optional[bool] = False,
    app: Optional[App] = None,
):
    """
    If the ``dry_run`` mode is enabled,
    the message will not be actually delivered to the recipients.
    Instead FCM performs all the usual validations, and emulates the send operation.
    """
    # [START send_to_token]
    # This registration token comes from the client FCM SDKs.
    # See documentation on defining a message payload.
    # condition = "'stock-GOOG' in topics || 'industry-tech' in topics"

    message = messaging.Message(
        data=data,
        token=token,
        notification=notification,
        android=android,
        webpush=webpush,
        apns=apns,
        fcm_options=fcm_options,
        topic=topic,
        condition=condition,
    )
    return messaging.send(message, dry_run, app=app)


def send_multicast_and_handle_errors(
    tokens: List[str],
    data: Optional[Dict[str, str]] = None,
    notification: Optional[messaging.Notification] = None,
    android: Optional[messaging.AndroidConfig] = None,
    webpush: Optional[messaging.WebpushConfig] = None,
    apns: Optional[messaging.APNSConfig] = None,
    fcm_options: Optional[messaging.FCMOptions] = None,
    dry_run: Optional[bool] = False,
    app: Optional[App] = None,
):
    """
    If the ``dry_run`` mode is enabled,
    the message will not be actually delivered to the recipients.
    Instead FCM performs all the usual validations, and emulates the send operation.
    """
    message = messaging.MulticastMessage(
        data=data,
        tokens=tokens,
        notification=notification,
        android=android,
        webpush=webpush,
        apns=apns,
        fcm_options=fcm_options,
    )
    response = messaging.send_multicast(message, dry_run=dry_run, app=app)
    if response.failure_count > 0:
        responses = response.responses
        failed_tokens = [
            tokens[idx] for idx, resp in enumerate(responses) if not resp.success
        ]

        print("List of tokens that caused failures: {0}".format(failed_tokens))
    return response


def subscribe_to_topic(tokens: List[str], topic: str):
    # [START subscribe]
    # These registration tokens come from the client FCM SDKs.

    # Subscribe the devices corresponding to the registration tokens to the
    # topic.
    response = messaging.subscribe_to_topic(tokens, topic)
    # See the TopicManagementResponse reference documentation
    # for the contents of response.
    print(response.success_count, "tokens were subscribed successfully")
    return response
    # [END subscribe]


def unsubscribe_from_topic(registration_tokens: List[str], topic: str):
    # [START unsubscribe]
    # These registration tokens come from the client FCM SDKs.
    # Unubscribe the devices corresponding to the registration tokens from the
    # topic.
    response = messaging.unsubscribe_from_topic(registration_tokens, topic)
    # See the TopicManagementResponse reference documentation
    # for the contents of response.
    print(response.success_count, "tokens were unsubscribed successfully")
    return response
    # [END unsubscribe]


def send_all(messages: List[messaging.Message]):
    # [START send_all]
    # Create a list containing up to 500 messages.
    response = messaging.send_all(messages)
    # See the BatchResponse reference documentation
    # for the contents of response.
    print("{0} messages were sent successfully".format(response.success_count))
    return response
    # [END send_all]
