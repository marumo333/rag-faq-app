-- クォータカウントをアトミックにデクリメントする関数
CREATE OR REPLACE FUNCTION decrement_quota_count(p_user_id UUID)
RETURNS void AS $$
BEGIN
    UPDATE user_quotas
    SET 
        remaining_count = remaining_count - 1,
        updated_at = NOW()
    WHERE 
        user_id = p_user_id 
        AND remaining_count > 0;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Quota not found or already at zero for user_id: %', p_user_id;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 月次リセット用の関数
CREATE OR REPLACE FUNCTION reset_expired_quotas()
RETURNS INTEGER AS $$
DECLARE
    reset_count INTEGER := 0;
BEGIN
    UPDATE user_quotas
    SET 
        remaining_count = CASE 
            WHEN plan_type = 'free' THEN 3
            WHEN plan_type = 'standard' THEN 15
            ELSE remaining_count
        END,
        reset_date = NOW() + INTERVAL '1 month',
        updated_at = NOW()
    WHERE 
        reset_date <= NOW();
    
    GET DIAGNOSTICS reset_count = ROW_COUNT;
    RETURN reset_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;