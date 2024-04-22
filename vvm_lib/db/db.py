import pandas as pd
import psycopg2
import io
import pymssql


class DB:
    """
    Класс для работы с базами данных postgresql и mssql для моего личного пользования
    """
    def __init__(self, dbname, user, password, port, host, what_db='postgresql'):
        """
        :param dbname: Название БД
        :param user: пользователь
        :param password: пароль
        :param port: порт
        :param host: хост
        :param what_db: 'postgresql' или 'mssql'
        """
        self.dbname = dbname
        self.user = user
        self.password = password
        self.port = port
        self.host = host
        self.what_db = what_db

    def open_connect(self):
        """
        :return: объект соединения
        """
        if self.what_db == 'postgresql':
            return psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password
                                    , port=self.port, host=self.host)
        elif self.what_db == 'mssql':
            return pymssql.connect(server=self.dbname, user={self.user}, password=self.password
                                   , port=self.port, host=self.host)

    @staticmethod
    def close_connect(connect):
        """
        :param connect:
        :return: закрытие соединения
        """
        connect.close()
        # print(f"Соединение закрыто")

    def select(self, sql: str):
        """
        Если нужно получить DATAFRAME
        :param sql: запрос SQL
        :return: pd.Dastaframe
        """
        connect = self.open_connect()
        try:
            with connect.cursor() as cursor:
                cursor.execute(sql)
                if self.what_db == 'postgresql':
                    result = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
                elif self.what_db == 'mssql':
                    result = pd.DataFrame([row for row in cursor.fetchall()])
        except psycopg2.ProgrammingError as error:
            raise print(error)
        finally:
            self.close_connect(connect)
        return result

    def insert(self, df: pd.DataFrame, table: str):
        """
        Вставка данных
        :param df:
        :param table:
        :return:
        """
        csv_io = io.StringIO()
        df.to_csv(csv_io, sep='\t', header=False, index=False)
        csv_io.seek(0)
        connect = self.open_connect()
        with connect.cursor() as cursor:
            cursor.copy_expert(f"""COPY {table} {str(tuple(df.columns)).replace("'", '"')} FROM STDIN  with (
                                        format csv,delimiter '\t', force_null {str(tuple(df.columns))})""", csv_io)
            cursor.commit()
        self.close_connect(connect)
        print(f'Данные успешно записаны в {table} объем {len(df)} - cursor.rowcount {cursor.rowcount}')

    def arbitrary_request(self, sql: str, query_name: str):
        """
        Свободный запрос без возврата данных
        :param sql: запрос
        :param query_name: название запроса
        :return: print
        """
        connect = self.open_connect()
        try:
            with connect.cursor() as cursor:
                cursor.execute(sql)
                connect.commit()
        except psycopg2.ProgrammingError as error:
            raise print(error)
        finally:
            self.close_connect(connect)
        print(f'Запрос выполнен {query_name}')

    def drop(self, table_name: str):
        """
        Удаление таблицы
        :param table_name: название таблицы со схемой
        :return: print()
        """
        connect = self.open_connect()
        try:
            with connect.cursor() as cursor:
                cursor.execute(f'drop table {table_name}')
                connect.commit()
        except psycopg2.ProgrammingError as error:
            raise print(error)
        finally:
            self.close_connect(connect)
        print(f'Таблица {table_name} удалена')

    def grand(self, table_name: str, users: list):
        """
        Для предоставление прав на чтение
        :param table_name: название таблицы
        :param users: список пользователей, которым надо предоставить доступ
        :return: print()
        """
        connect = self.open_connect()
        try:
            with connect.cursor() as cursor:
                cursor.execute(f'grant select on {table_name} to {",".join(users)}')
                connect.commit()
        except psycopg2.ProgrammingError as error:
            raise print(error)
        finally:
            self.close_connect(connect)
        print(f'grant select к таблице {table_name} предоставлен для {" ,".join(users)}')

    def truncate(self, table_name: str):
        """
        truncate таблицы
        :param table_name: название таблицы
        :return:  print()
        """
        connect = self.open_connect()
        try:
            with connect.cursor() as cursor:
                cursor.execute(f'truncate table  {table_name}')
                connect.commit()
        except psycopg2.ProgrammingError as error:
            raise print(error)
        finally:
            self.close_connect(connect)
        print(f'Таблица {table_name} очищена')
