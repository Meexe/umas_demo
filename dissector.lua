modbus_proto = Proto("modbustcp", "Modbus TCP")
umas_proto = Proto("umas", "UMAS Modbus")

function umas_proto.dissector(buffer, pinfo, tree)
    local modbus_tree = tree:add(modbus_proto, buffer(),"Modbus Data Protocol")
    if buffer(2, 2):uint() ~= 0 then
        if buffer(7, 1):uint() ~= 90 then
            return
        end
    end
    pinfo.cols.protocol = "UMAS"

    modbus_tree:add(buffer(0, 2), "Transaction ID: " .. buffer(0, 2))
    modbus_tree:add(buffer(2, 2), "Protocol ID: " .. buffer(2, 2))
    modbus_tree:add(buffer(4, 2), "Length: " .. buffer(4, 2))
    modbus_tree:add(buffer(6, 1), "Slave address: " .. buffer(6, 1))
    modbus_tree:add(buffer(7, 1), "Function code: " .. buffer(7, 1))

    local umas_tree = modbus_tree:add(umas_proto, buffer(),"UMAS Data Protocol")
    umas_tree:add(buffer(8, 1), "Owner: " .. buffer(8, 1))
    if buffer(9, 1):uint() == 2 then umas_tree:add(buffer(9, 1), "UMAS code READ_ID: " .. buffer(9, 1))
        elseif buffer(9, 1):uint() == 16 then umas_tree:add(buffer(9, 1), "UMAS code TAKE_RESERVATION: " .. buffer(9, 1))
        elseif buffer(9, 1):uint() == 17 then umas_tree:add(buffer(9, 1), "UMAS code RELEASE_RESERVATION: " .. buffer(9, 1))
        elseif buffer(9, 1):uint() == 18 then umas_tree:add(buffer(9, 1), "UMAS code KEEP_ALIVE: " .. buffer(9, 1))
        elseif buffer(9, 1):uint() == 254 then umas_tree:add(buffer(9, 1), "UMAS response OK: " .. buffer(9, 1))
        elseif buffer(9, 1):uint() == 253 then umas_tree:add(buffer(9, 1), "UMAS response Error: " .. buffer(9, 1))
    end
    if buffer:len() > 10 then
        umas_tree:add(buffer(10, buffer:len()-10), "UMAS payload " .. buffer(10, buffer:len()-10))
    end
end

tcp_table = DissectorTable.get("tcp.port")
tcp_table:add(10001, umas_proto)
