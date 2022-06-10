import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

from models.item import ItemModel


class Item(Resource):
    
    parser = reqparse.RequestParser()
    parser.add_argument('price', 
                        type=float, 
                        required=True, 
                        help='This field cannot be left blank!')
        
    
    @jwt_required() # authentification needed
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item: return item.json()
        return {'message': 'Item not found!'}, 404
    
    
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': 'An item with name "{}" already exists.'.format(name)}, 400
        
        data = Item.parser.parse_args()
        
        item = ItemModel(name, data['price'])
        
        try:
            item.insert()
        except:
            return {'message': 'An error occurred inserting the item.'}, 500
        
        return item.json(), 201
    
    
    def delete(self, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        
        query = "DELETE FROM items WHERE name=?"
        cursor.execute(query, (name,))
        
        connection.commit()
        connection.close()
        
        return {'message': 'Item deleted'}
    
    
    def put(self, name):
        data = Item.parser.parse_args()
        
        item = ItemModel.find_by_name(name)
        updated = ItemModel(name, data['price'])
        
        if not item:
            try:
                updated.insert()
            except:
                return {'message': 'An error occurred inserting the item.'}, 500
        else:
            try:
                updated.update()
            except:
                return {'message': 'An error occurred updating the item.'}, 500
        return updated.json()
    


class ItemList(Resource):
    def get(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        
        query = "SELECT * FROM items"
        result = cursor.execute(query)
        items = []
        
        for row in result:
            items.append({'name': row[0], 'price': row[1]})
        
        connection.close()
        
        return {'item': items}