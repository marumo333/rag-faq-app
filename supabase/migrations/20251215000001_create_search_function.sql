-- ベクトル類似度検索用のPostgreSQL関数
CREATE OR REPLACE FUNCTION search_embeddings(
    query_embedding vector(768),
    match_count int DEFAULT 5,
    filter_tenant_id uuid DEFAULT NULL
)
RETURNS TABLE (
    chunk_id uuid,
    document_id uuid,
    content text,
    section text,
    similarity float,
    document_title text
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id as chunk_id,
        c.document_id,
        c.content,
        c.section,
        1 - (e.embedding <=> query_embedding) as similarity,
        d.title as document_title
    FROM faq_embeddings e
    JOIN faq_chunks c ON e.chunk_id = c.id
    JOIN documents d ON c.document_id = d.id
    WHERE 
        (filter_tenant_id IS NULL OR d.tenant_id = filter_tenant_id)
        AND d.status = 'completed'
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- インデックスが存在することを確認（既にあるが念のため）
CREATE INDEX IF NOT EXISTS idx_embeddings_vector_cosine ON faq_embeddings 
USING hnsw (embedding vector_cosine_ops);

-- パフォーマンス向上のためのインデックス
CREATE INDEX IF NOT EXISTS idx_documents_status_tenant ON documents(status, tenant_id);