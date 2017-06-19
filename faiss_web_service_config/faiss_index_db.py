
# init dir and sqlite connection
import sys
import os
import json
import numpy as np
import sqlite3
import faiss


def GET_FAISS_INDEX():
    # app = 'test_app'
    # if app and tenant and category:
    #     print "get index %s %s %s" % (app, tenant, category)
    #     index_file_path = dir_tenant_category(app, tenant, category)
    # elif app and tenant:
    #     print "get index %s %s" % (app, tenant)
    #     index_file_path = dir_tenant_all(app, tenant)
    # elif app:
    #     print "get index %s" % (app,)
    #     index_file_path = dir_all(app)
    # else:
    #     print "index not found"
    #     return
    import faiss
    import sys
    import os
    sys.path.append('/opt/faiss-web-service/faiss_web_service_config')
    import faiss_index_db as this_file
    index_path = this_file.dir_all('test_app')
    if not os.path.exists(index_path):
        return None
    return faiss.read_index(str(this_file.dir_all('test_app')))


def GET_FAISS_ID_TO_VECTOR():
    def id_to_vector(id_):
        try:
            cursor = conn.cursor()
            cursor.execute(''' SELECT * FROM FEATURE_QUEUE WHERE FEATURE_ID=? ''', (str(id_),))
            row = cursor.fetchone()
            if not row:

                return None
            feature = row['FEATURE']
            xb = np.array(json.loads(feature)).astype('float32')
            return xb
        except Exception, e:
            print e
            pass

    return id_to_vector


def GET_FAISS_RESOURCES():
    import sys
    sys.path.append('/opt/faiss-web-service/faiss_web_service_config')
    import faiss_index_db as this_file
    features = this_file.list_features()
    for i, row in enumerate(features):
        app = row['APP']
        tenant = row['TENANT']
        category = row['CATEGORY']
        feature_id = row['FEATURE_ID']
        feature = row['FEATURE']
        xb = np.array(json.loads(feature)).astype('float32')
        ids = [feature_id] * xb.shape[0]
        ids = np.array(ids).astype('int')
        print '---------------------------------------------- indexing...'
        print '%s %s %s' % (app, tenant, category)
        this_file.build_index(app, tenant, category, ids, xb)
        this_file.delete_feature(app, tenant, category, feature_id)
        print 'index finish.\n'


def PUT_FEATURE_QUEUE():
    def put_feature_queue(tenant, category, feature_id, feature):
        try:
            cursor = conn.cursor()
            cursor.execute(
                ''' INSERT INTO FEATURE_QUEUE(APP, TENANT, CATEGORY, FEATURE_ID, FEATURE) VALUES(?, ?, ?, ?, ?) ''',
                ('test_app', tenant, category, feature_id, feature))
            conn.commit()
        except Exception, e:
            print e
            pass
    return put_feature_queue


def delete_feature(app, tenant, category, feature_id):
    cursor = conn.cursor()
    cursor.execute(''' 
            UPDATE FEATURE_QUEUE SET STATUS='-99' WHERE APP=? AND TENANT=? AND CATEGORY=? AND FEATURE_ID=? 
        ''', (app, tenant, category, feature_id))
    conn.commit()


def list_features():
    cursor = conn.cursor()
    cursor.execute(''' SELECT * FROM FEATURE_QUEUE WHERE STATUS='10' ''')
    return cursor.fetchall()


def build_index(app, tenant, category, ids, xb):
    update_index_file(ids, xb, dir_all(app))
    update_index_file(ids, xb, dir_tenant_all(app, tenant))
    update_index_file(ids, xb, dir_tenant_category(app, tenant, category))


def update_index_file(ids, xb, index_file):
    if os.path.exists(index_file):
        index = faiss.read_index(index_file)
    else:
        index = faiss.IndexFlatL2(xb.shape[1])  # simple index
    index.train(xb)
    index_with_ids = faiss.IndexIDMap(index)
    index_with_ids.add_with_ids(xb, ids)
    index_file_dir = os.path.split(index_file)[0]
    if not os.path.isdir(index_file_dir):
        os.makedirs(index_file_dir)
    faiss.write_index(index_with_ids, str(index_file))


def init_table():
    try:
        cursor = conn.cursor()
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS FEATURE_QUEUE (
                    APP            CHAR(128) NOT NULL,
                    TENANT         CHAR(128) NOT NULL,
                    CATEGORY       CHAR(128) NOT NULL,
                    FEATURE_ID     CHAR(128) NOT NULL,
                    FEATURE        TEXT NOT NULL,
                    STATUS         INT DEFAULT 10
                )
                ''')
        conn.commit()
        print 'Create table success'
    except Exception, e:
        print 'Create table failed'
        print e.message
        conn.close()
        sys.exit(1)


def dir_all(app):
    return "%s/index/app_%s/all.index" % (tmp_folder, app)


def dir_tenant_all(app, tenant):
    return "%s/index/app_%s/tenant_%s/all.index" % (tmp_folder, app, tenant)


def dir_tenant_category(app, tenant, category):
    return "%s/index/app_%s/tenant_%s/category_%s.index" % (tmp_folder, app, tenant, category)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# init
tmp_folder = "/opt/faiss-web-service/my_index_files"
if not os.path.exists(tmp_folder):
    os.makedirs(tmp_folder)
conn = sqlite3.connect(tmp_folder + '/feature_queue.db')
conn.row_factory = dict_factory

mxb_txt = open('/opt/faiss-web-service/mxb.txt')
try:
    mxb = mxb_txt.read()
finally:
    mxb_txt.close()

init_table()
put_feature_queue = PUT_FEATURE_QUEUE()
put_feature_queue('test_tenant', 'FABRIC', '987654321', mxb)
UPDATE_FAISS_AFTER_SECONDS = 60 * 60  # every hour
