from sqlalchemy import create_engine, text
engine = create_engine('postgresql://postgres:postgres@localhost:5432/git_graph_dev')
with engine.connect() as conn:
    print('Entities count:', conn.execute(text('select count(*) from code_entities')).scalar())
    print('Versions count:', conn.execute(text('select count(*) from entity_versions')).scalar())
    print('Commits count:', conn.execute(text('select count(*) from commits')).scalar())
    print('Source files count:', conn.execute(text('select count(*) from source_files')).scalar())
    
    entity_id = 'e3d116f1-62ed-50f3-b101-94bcbedd2dfe'
    print('\nEntity in code_entities:')
    for row in conn.execute(text(f"select seid, name, qualified_name, repository_id from code_entities where seid = '{entity_id}'")):
        print(row)
    print('\nEntity in entity_versions:')
    for row in conn.execute(text(f"select id, seid, commit_hash, version_ordinal, canonical_name from entity_versions where seid = '{entity_id}'")):
        print(row)
