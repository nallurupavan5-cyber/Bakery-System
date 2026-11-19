def test_registration(client):
    response = client.post('/auth/register', data={
        'name': 'Alice Wonder',
        'username': 'alice',
        'phone': '+1 555-9988',
        'email': 'alice@wonder.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'address': '42 Rabbit Hole Lane'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Account created successfully' in response.data


def test_login_success(auth):
    response = auth.login('customer', 'customer123')
    assert response.status_code == 200
    assert b'Welcome back, customer!' in response.data


def test_login_invalid_credentials(auth):
    response = auth.login('customer', 'wrongpassword')
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data


def test_customer_unauthorized_from_admin(auth, client):
    auth.login('customer', 'customer123')
    # Customer accessing admin route should get 403 Forbidden
    response = client.get('/admin/dashboard')
    assert response.status_code == 403
    assert b'403' in response.data or b'Forbidden' in response.data


def test_customer_unauthorized_from_pos(auth, client):
    auth.login('customer', 'customer123')
    response = client.get('/cashier/pos')
    assert response.status_code == 403


def test_admin_authorized(auth, client):
    auth.login('admin', 'admin123')
    response = client.get('/admin/dashboard')
    assert response.status_code == 200
    assert b'Administrator Command Center' in response.data


def test_cashier_authorized(auth, client):
    auth.login('cashier', 'cashier123')
    response = client.get('/cashier/pos')
    assert response.status_code == 200
    assert b'Cashier POS Terminal' in response.data


def test_baker_authorized(auth, client):
    auth.login('baker', 'baker123')
    response = client.get('/baker/dashboard')
    assert response.status_code == 200
    assert b'Kitchen Display System' in response.data


def test_store_keeper_authorized(auth, client):
    auth.login('store', 'store123')
    response = client.get('/inventory/dashboard')
    assert response.status_code == 200
    assert b'Raw Material Inventory' in response.data
