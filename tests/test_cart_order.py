def test_cart_workflow(client):
    # 1. Add item
    res = client.post('/cart/add', data={'product_id': '1', 'quantity': '2'}, follow_redirects=True)
    assert res.status_code == 200
    assert b'Added 2x' in res.data or b'Your Fresh Bakery Cart' in res.data

    # 2. View cart
    res = client.get('/cart')
    assert res.status_code == 200
    assert b'Chocolate Truffle Cake' in res.data
    assert b'57.00' in res.data  # 2 x 28.50

    # 3. Increase quantity
    res = client.post('/cart/update', data={'product_id': '1', 'action': 'increase'}, follow_redirects=True)
    assert res.status_code == 200
    assert b'85.50' in res.data  # 3 x 28.50

    # 4. Remove item
    res = client.post('/cart/remove/1', follow_redirects=True)
    assert res.status_code == 200
    assert b'Your Bakery Cart is Empty' in res.data


def test_checkout_and_order_creation(auth, client):
    auth.login('customer', 'customer123')

    # Add item to cart
    client.post('/cart/add', data={'product_id': '1', 'quantity': '1'}, follow_redirects=True)

    # Checkout
    response = client.post('/checkout', data={
        'name': 'Test Customer',
        'phone': '+1 555-0100',
        'email': 'test@cust.com',
        'address': '123 Bakery Lane',
        'payment_mode': 'Cash',
        'special_instructions': 'Fragile delivery'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'placed successfully' in response.data or b'Real-Time Order Tracking' in response.data


def test_custom_cake_order_creation(auth, client):
    auth.login('customer', 'customer123')

    response = client.post('/custom-cake', data={
        'name': 'Test Customer',
        'phone': '+1 555-0100',
        'email': 'test@cust.com',
        'cake_type': 'Wedding Fondant Cake',
        'flavour': 'Vanilla Bean & Berries',
        'size': '2.0 kg',
        'quantity': '1',
        'required_date': '2026-12-25',
        'required_time': '2:00 PM',
        'design_notes': 'Silver beads with white ribbon',
        'special_instructions': 'Eggless'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Custom cake order request' in response.data or b'Order History' in response.data
