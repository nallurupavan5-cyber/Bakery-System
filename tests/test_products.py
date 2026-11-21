def test_menu_page(client):
    response = client.get('/menu')
    assert response.status_code == 200
    assert b'Artisan Bakery Catalog' in response.data
    assert b'Chocolate Truffle Cake' in response.data


def test_product_search(client):
    response = client.get('/menu?search=Truffle')
    assert response.status_code == 200
    assert b'Chocolate Truffle Cake' in response.data


def test_product_details_page(client):
    response = client.get('/product/1')
    assert response.status_code == 200
    assert b'Chocolate Truffle Cake' in response.data
    assert b'28.50' in response.data


def test_admin_create_product(auth, client):
    auth.login('admin', 'admin123')
    response = client.post('/admin/products/add', data={
        'name': 'Artisan Baguette',
        'category_id': '1',
        'price': '4.50',
        'description': 'Crispy French crust baguette',
        'availability': '1'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Artisan Baguette' in response.data


def test_admin_edit_product(auth, client):
    auth.login('admin', 'admin123')
    response = client.post('/admin/products/1/edit', data={
        'name': 'Deluxe Chocolate Truffle Cake',
        'category_id': '1',
        'price': '32.00',
        'description': 'Updated description',
        'availability': '1'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Deluxe Chocolate Truffle Cake' in response.data
