import aiomysql
import os

class Database:
    def __init__(self):
        self.pool = None

    async def setup(self):
        """Inicializa o pool de conexões com o MySQL usando variáveis de ambiente."""
        try:
            host = os.getenv("DB_HOST")
            print(f"[DB] Tentando conectar ao host: {host}")
            
            self.pool = await aiomysql.create_pool(
                host=host,
                port=int(os.getenv("DB_PORT", 3306)),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASS"),
                db=os.getenv("DB_NAME"),
                autocommit=True,
                cursorclass=aiomysql.DictCursor,
                minsize=1,
                maxsize=5,
                pool_recycle=300
            )
            print("[DB] Conexao com o banco de dados MySQL estabelecida!")
        except Exception as e:
            print(f"[DB] Erro ao conectar ao banco de dados: {e}")
            raise e

    async def get_existing_tables(self):
        """Busca os nomes de todas as tabelas existentes no banco de dados atual."""
        try:
            rows = await self.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()")
            existing = set()
            for row in rows:
                for val in row.values():
                    if val:
                        existing.add(str(val).lower())
            return existing
        except Exception as e:
            print(f"[DB] Aviso ao consultar tabelas existentes: {e}")
            return set()

    async def create_tables(self):
        """Verifica quais tabelas ja existem e apenas cria as que estiverem faltando."""
        existing_tables = await self.get_existing_tables()
        
        # Tabela botsettings
        if "botsettings" not in existing_tables:
            print("[DB] Tabela 'botsettings' nao encontrada. Criando...")
            await self.execute("""
                CREATE TABLE botsettings (
                    guild_id BIGINT PRIMARY KEY,
                    serverprefix VARCHAR(5) DEFAULT '.'
                )
            """)
            print("[DB] Tabela 'botsettings' criada com sucesso.")
        else:
            print("[DB] Tabela 'botsettings' ja existe. Ignorando criacao.")

        # Tabela leagueconfig
        if "leagueconfig" not in existing_tables:
            print("[DB] Tabela 'leagueconfig' nao encontrada. Criando...")
            await self.execute("""
                CREATE TABLE leagueconfig (
                    user_id BIGINT PRIMARY KEY,
                    riot_id VARCHAR(100) NOT NULL
                )
            """)
            print("[DB] Tabela 'leagueconfig' criada com sucesso.")
        else:
            print("[DB] Tabela 'leagueconfig' ja existe. Ignorando criacao.")

    async def execute(self, query, params=None):
        """Executa comandos como INSERT, UPDATE, DELETE."""
        for attempt in range(2):
            try:
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(query, params or ())
                        return cur.rowcount
            except aiomysql.OperationalError as e:
                if attempt == 0 and e.args[0] in (2006, 2013):
                    continue
                raise e

    async def fetch(self, query, params=None):
        """Busca múltiplos registros (SELECT)."""
        for attempt in range(2):
            try:
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(query, params or ())
                        return await cur.fetchall()
            except aiomysql.OperationalError as e:
                if attempt == 0 and e.args[0] in (2006, 2013):
                    continue
                raise e

    async def fetch_one(self, query, params=None):
        """Busca um único registro."""
        for attempt in range(2):
            try:
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(query, params or ())
                        return await cur.fetchone()
            except aiomysql.OperationalError as e:
                if attempt == 0 and e.args[0] in (2006, 2013):
                    continue
                raise e
