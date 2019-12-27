modbus_proto = Proto("modbus","")
umas_proto = Proto("umas","UMAS Modbus")

function umas_proto.dissector(buffer,pinfo,tree)
    local subtree = tree:add(umas_proto,buffer(),"UMAS Protocol Data")
    if buffer(7,1):uint() ~= 90 then
        return
    end
    pinfo.cols.protocol = "UMAS"

    subtree:add(buffer(8,1),"owned_counter: " .. buffer(8,1):int())

    if buffer(9,1):uint() == 2 then subtree:add(buffer(9,1),"UMAS code READ_ID: " .. buffer(9,1):int())
        elseif buffer(9,1):uint() == 16 then subtree:add(buffer(9,1),"UMAS code TAKE_RESERVATION: " .. buffer(9,1):uint())
        elseif buffer(9,1):uint() == 17 then subtree:add(buffer(9,1),"UMAS code RELEASE_RESERVATION: " .. buffer(9,1):uint())
        elseif buffer(9,1):uint() == 18 then subtree:add(buffer(9,1),"UMAS code KEEP_ALIVE: " .. buffer(9,1):uint())
        elseif buffer(9,1):uint() == 254 then subtree:add(buffer(9,1),"UMAS response OK")
    end

    if buffer:len() > 10 then
        subtree:add(buffer(10,buffer:len()-10),"UMAS payload " .. buffer(10,buffer:len()-10))
    end

end
tcp_table = DissectorTable.get("tcp.port")
tcp_table:add(10001,umas_proto)
