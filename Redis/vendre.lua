local stock = tonumber(redis.call("GET", KEYS[1]))
if stock and stock > 0 then
    return redis.call("DECR", KEYS[1])
end
return -1
