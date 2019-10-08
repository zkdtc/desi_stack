import os
from __init__ import create_app
import db
app=create_app()
#print(os.path.exists(os.path.join(app.instance_path,'desi_stack.sqlite')))

#if not os.path.exists(os.path.join(app.instance_path,'desi_stack.sqlite')):
#    with app.app_context():
#        db.init_db()
#with app.app_context():
#    db.init_db()

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')

