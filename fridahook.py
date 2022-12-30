import sys
from base64 import b64decode

import frida

sys.path.append("server")
from server.constants import CONFIG_PATH
from server.utils import read_json

server = read_json(CONFIG_PATH)["server"]
HOST = server["host"]
PORT = server["port"]
MODE = server["mode"]

def on_message(message, data):
    print("[%s] => %s" % (message, data))

def main():
    device = frida.get_usb_device(timeout=1)
    while True:
        num = input("Choose your connection.\n1. Attach Directly\n2. Spawn and Attach\nChoose one: ")
        try:
            num = int(num)
        except:
            print("Invalid input")
            continue

        if num not in [1, 2]:
            print("Invalid input")
            continue

        if MODE == "cn":
            TRUE_ADD = "0x1b87621, 0xbe735a, 0x4c6f851, 0xbe74a0"
            FALSE_ADD = "0x1b7fcc9"
        elif MODE == "global":
            TRUE_ADD = "0x03208494, 0x04225acc, 0x04225bf0, 0x051c4fe4, 0x051c7cf4, 0x021a95e4"
            FALSE_ADD = "0x021a25dc"

        if num == 1:
            session = device.attach("Arknights")
            java_session = device.attach("Arknights")
            timeout = 500
            break

        elif num == 2:
            if MODE == "cn":
                pid = device.spawn(b64decode('Y29tLmh5cGVyZ3J5cGguYXJrbmlnaHRz').decode())
                device.resume(pid)
                session = device.attach(pid)
                java_session = device.attach(pid)
            elif MODE == "global":
                pid = device.spawn(b64decode('Y29tLllvU3RhckVOLkFya25pZ2h0cw==').decode())
                device.resume(pid)
                session = device.attach(pid, realm="emulated")
                java_session = device.attach(pid)
            timeout = 6000
            break

    java_script = java_session.create_script("""

    function redirect_traffic_to_proxy(proxy_url, proxy_port) {{
        Java.perform(function (){{
            console.log("[.] Traffic Redirection");
            var url = Java.use("java.net.URL");
            var proxyTypeI = Java.use('java.net.Proxy$Type');
            var inetSockAddrWrap = Java.use("java.net.InetSocketAddress");
            var proxy = Java.use('java.net.Proxy');

            url.$init.overload('java.lang.String').implementation = function (var0) {{
                const urls = [
                    'android.bugly.qq.com',
                    'ak-conf.hypergryph.com',
                    'ak-conf.arknights.global',
                    'bi-track.hypergryph.com',
                    'down.anticheatexpert.com',
                    'passport.arknights.global:443',
                    'passport.arknights.global',
                    'log.trackingio.com',
                    'wkdcm2.tingyun.com'
                ];
                urls.forEach(function (url) {{
                    if(var0.match(url)) {{
                        var0 = var0.replace(url, proxy_url + ":" + proxy_port).replace("https", "http");
                        console.log("[*] Created new URL with value: " + var0);
                    }}
                }})
                return this.$init(var0);
            }};

            url.openConnection.overload().implementation = function () {{
                var proxyImpl;

                try{{
                    proxyImpl = proxy.$new(proxyTypeI.valueOf('HTTP'), inetSockAddrWrap.$new(proxy_url, proxy_port));
                }}
                catch(e){{
                    console.log(e);
                }}

                return this.openConnection(proxyImpl);
            }};
        }});
    }}

    function init(){{
        var proxy_url = "{HOST}";
        var proxy_port = {PORT};
        redirect_traffic_to_proxy(proxy_url, proxy_port);
    }}

    init();

""".format(HOST=HOST, PORT=PORT))
    java_script.on('message', on_message)
    java_script.load()

    script = session.create_script("""
    function get_func_by_offset(offset){{
        var module = Process.getModuleByName("libil2cpp.so");
        var addr = module.base.add(offset);
        return new NativePointer(addr.toString());
    }}

    function hookTrue(address) {{
        var func = get_func_by_offset(address);
        console.log('[+] Hooked True Function: ' + func.toString());
        Interceptor.attach(func,{{
            onEnter: function(args){{}},
            onLeave: function(retval){{
                retval.replace(0x1);
            }}
        }});
    }}

    function hookFalse(address) {{
        var func = get_func_by_offset(address);
        console.log('[+] Hooked False Function: ' + func.toString());
        Interceptor.attach(func,{{
            onEnter: function(args){{}},
            onLeave: function(retval){{
                retval.replace(0x0);
            }}
        }});
    }}

    function hookDump(address) {{
        var func = get_func_by_offset(address);
        console.log('[+] Hooked Dump Function: ' + func.toString());
        Interceptor.attach(func,{{
            onEnter: function(args){{
                console.log(typeof(Memory.readCString(args[0])));
                console.log(Memory.readCString(args[0]));
                console.log(args[0]);
                console.log(typeof(Memory.readCString(args[1])));
                console.log(args[1].readCString());
                console.log(args[1]);
            }},
            onLeave: function(retval){{
                //console.log('[!!] Hooked Dump Function: ' + Number(address).toString(16) + ' Return Value: ' + retval.readCString());
                console.log('[!!] Hooked Dump Function: ' + Number(address).toString(16) + ' Return Value: ' + retval);
            }}
        }});
    }}

    function init(){{
        setTimeout(function() {{
            [{TRUE_ADD}].forEach(hookTrue);
            [{FALSE_ADD}].forEach(hookFalse);
        }}, {timeout});
    }}

    init();

""".format(timeout=timeout, TRUE_ADD=TRUE_ADD, FALSE_ADD=FALSE_ADD))
    script.on('message', on_message)
    script.load()
    print("[!] Ctrl+D on UNIX, Ctrl+Z on Windows/cmd.exe to detach from instrumented program.\n\n")
    sys.stdin.read()
    session.detach()

if __name__ == '__main__':
    main()
