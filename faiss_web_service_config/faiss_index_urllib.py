def GET_FAISS_RESOURCES():  # TODO: read new xb, d from mysql
    import sqlite3

    # create base dir
    tmp_folder = '/opt/faiss-web-service/my_index_files'
    if not os.path.exists(tmp_folder):
        os.makedirs(tmp_folder)

    # read index from sqlite
    conn = sqlite3.connect(tmp_folder + '/feature_queue.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS FEATURE_QUEUE (
                ID             INTEGER   NOT NULL AUTOINCREMENT PRIMARY KEY,
                APP_ID         CHAR(128) NOT NULL,
                TENANT_ID      CHAR(128) NOT NULL,
                CATEGORY       CHAR(128) NOT NULL,
                FEATURE             TEXT
            );
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS INDEX_CONFIG (
                K         VARCHAR(128) PRIMARY KEY,
                V         VARCHAR(128) NOT NULL,
            );
            ''')
        conn.commit()
    except Exception, e:
        print 'Create table failed'
        print e.message
        conn.close()
        return
    cursor.execute(''' SELECT * FROM INDEX_CONFIG WHERE K='DIMENSION' ''')
    configs = cursor.fetchall()
    if len(configs) > 0:
        print configs[0]
    else:
        print 'Has not config DIMENSION in INDEX_CONFIG table'
        return

    # build index
    dimension = ??
    app = ??
    tenant = ??
    category = ??
    xb = ??

    update_index_file(dimension, xb, tmp_folder + '/index/' + app + '/all')
    update_index_file(dimension, xb, tmp_folder + '/index/' + app + '/' + tenant + '/all')
    update_index_file(dimension, xb, tmp_folder + '/index/' + app + '/' + tenant + '/' + category)



def update_index_file(dimension, xb, index_file):
    import os
    import faiss

    #  load index
    if os.path.exists(index_file):
        index = faiss.read_index(index_file)
    else:
        index = faiss.IndexFlatL2(dimension)  # simple index
    index.train(xb)
    index.add(xb)
    faiss.write_index(index, index_file)

def GET_FAISS_INDEX():
    import faiss

    index_file_path = '/tmp/faiss-web-service/index'
    return faiss.read_index(index_file_path)


def GET_FAISS_ID_TO_VECTOR():
    import pickle

    ids_vectors_path = '/tmp/faiss-web-service/ids_vectors.p'
    with open(ids_vectors_path, 'rb') as f:
        ids_vectors = pickle.load(f)

    def id_to_vector(id_):
        try:
            return ids_vectors[id_]
        except:
            pass

    return id_to_vector


UPDATE_FAISS_AFTER_SECONDS = 60 * 60  # every hour
