from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text
import psycopg2
from urllib.parse import quote
from DetoxProject.system_sever_set import db_server
    
class DatabaseConnect():
    # db 연결하기
    def __init__(self):
        self.dbname = db_server.dbname
        self.dbuser = db_server.dbuser
        self.dbpassword = db_server.dbpassword
        self.host = db_server.host

        # self.dbname = "survey_test"
        # self.dbuser = "postgres"
        # self.dbpassword = "adminadmin"
        # self.host = "localhost"

        self.db = psycopg2.connect(host=self.host, dbname=self.dbname, 
                                   user=self.dbuser, password=self.dbpassword, port=5432)
        self.cursor=self.db.cursor()

    def __del__(self):
        self.db.close()
        self.cursor.close()

    #sql 명령 처리 함수 (조회빼고)
    def execute(self, query, args={}):
        self.cursor.execute(query,args)
 
    #sql 조회 명령 처리 함수
    def Readexecute(self, query, args={}):
        self.cursor.execute(query,args)
        row = self.cursor.fetchall()
        return row
    
    #db 트랜잭션 변화 커밋 처리 함수
    def commit(self):
        self.db.commit()

class CRUD(DatabaseConnect):

    def insertDB(self, table, col, data):
        sql = " INSERT INTO {table}({col}) VALUES({data});".format(table=table, col=col, data=data)
        print(sql)
        try:
            self.execute(sql)
            self.commit()
            result = "Succeed!"
        except Exception as e:
            result = (" insert DB err",e)
                      
        return result
       
    def readDB(self, col, table):
        sql = " SELECT {col} FROM {table};".format(col=col, table=table)
        try:
            result = self.Readexecute(sql)
        except Exception as e:
            result = (" read DB err",e)
                      
        return result

    def updateDB(self, table, col, data, condition):
        sql = " UPDATE {table} SET {col}='{data}' WHERE {col}={condition};".format(table=table, col=col, data=data, condition=condition)
        try:
            result = self.execute(sql)
            self.commit()
            result = "Succeed!"
        except Exception as e:
            result = (" update DB err",e)
                      
        return result
               
    def deleteDB(self, table, condition):
        sql = " DELETE FROM {table} WHERE {condition};".format(table=table, condition=condition)
        print(sql)
        try:
            self.execute(sql)
            self.commit()
            result = "Succeed!"
        except Exception as e:
            result = (" delete DB err",e)
                      
        return result
    
    def sql_cud(self,sql):
        print(sql)
        try:
            self.execute(sql)
            self.commit()
            result = "Succeed!"
        except Exception as e:
         result = (" DB err",e)
                    
        return result

    def sql_read(self, sql):
        try:
            result = self.Readexecute(sql)
        except Exception as e:
            result = (" read DB err",e)
                    
        return result

class dbSqlAlchemy():
  
    def get_engine():
        dbinfo = DatabaseConnect()
        dbuser = dbinfo.dbuser
        dbpassword = quote(dbinfo.dbpassword)
        host = dbinfo.host
        dbname = dbinfo.dbname

        engine = create_engine(
            "postgresql://"+dbuser+":"+dbpassword+"@"+host+":5432/"+dbname
        )

        base = declarative_base()

        Session = sessionmaker(engine)
        session = Session()

        base.metadata.create_all(engine)

        return engine,session
    
# engine,session = dbSqlAlchemy.get_engine()
# query_execute =engine.connect()
# querytext = text("select user_sq from tb_user where user_id = 'dddddd' order by create_date desc limit 1;") #
# result = query_execute.execute(querytext).all()
# user_sq = result[0][0] #

# print(result)