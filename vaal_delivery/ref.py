Dear Sir, 
I am attaching the documentation for “vaal.me” application, as agreed and here is a suggested test scenario 

1. Create a test user and setup all the information for that business user.
2. Call the first endpoint URL https://api.vaal.me/api/auth.
3. Use the user credential created in step 1, and as described in the APIs documentation for the first endpoint.
4. Get the x-auth from the response in order to user it in the subsequent request.
5. Call the second endpoint [https://api.vaal.me/api/orders] to bulk load orders as described in the documentation, fill in the required properties in the request body, and use the x-auth from the first step in the header.
6. The orders should be created in the business_user_orders, check the records inserted their, then the API will insert the orders in the business_user_paid_amount, the tester should check the records inserted there also with valid values.
7. After that the API will create a tracking record for the orders as status=0.

Note: The API system is meant to replace the direct insertion from the clients to the vaal.me backend system, so after this process it will be the responsibility of the “vaal” admin to track and maintain the orders, their statuses and the delivery. Printing orders with bar codes and the rest of the system should be continued as usual since it is not affected by the APIs.

8. To check for a status for a particular order, [https://api.vaal.me/api/order/status/:id] providing the ID for the order.

9. If there is any API needed to be implemented please let us know to study it and check if we are able to do it.

User: wecare@baytonia.com 


123Bayt

Pass: 123Bayt