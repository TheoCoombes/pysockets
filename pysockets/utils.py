from ast import literal_eval

# Encodes an argument into bytes ready for sending through a socket.
def encode_arg(arg, encoding="utf-8"):
    if type(arg) is bytes:
        return "B".encode(encoding) + arg
    elif type(arg) is str:
        return "S{}".format(arg).encode(encoding)
    else:
        return str(arg).encode(encoding)

# Decodes an argument recieved from a socket into the original variable.
def decode_arg(arg, encoding="utf-8"):
    atype = arg[:1]
    if atype == b"B":
        return arg[1:]
    elif atype == b"S":
        return arg[1:].decode(encoding)
    else:
        return literal_eval(arg.decode(encoding))
    

# Encodes all arguments. See encode_arg
def encode_args(args, encoding="utf-8"):
    nargs = b""
    splits = []
    for arg in args:
        nargs += encode_arg(arg, encoding)
        splits.append(len(nargs))
    return nargs, splits

# Decodes all arguments. See decode_arg
def decode_args(data, splits, encoding="utf-8"):
    count = 0
    nargs = []
    for i in splits:
        nargs.append(decode_arg(data[count:i], encoding))
        count = i
    return tuple(nargs)

# Splits pure bytes into a splits array and the original data.
def decode_splits_data(odata, encoding="utf-8"):
    for i in range(4000): # Works; needs more reliable fix
        if odata[i:i+1] == b"]":
            splits = literal_eval(odata[0:i+1].decode(encoding))
            data = odata[i+1:]
            break
    return data, splits
