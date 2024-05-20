# Bevy2Flask 0.0.0 (BevyFrame 0.2 ɑ)

The module that plays between Flask and BevyFrame to let people use their apps in production using any WSGI runtime out there.

Please visit [BevyFrame](https://github.com/islekcaganmert/bevyframe) for information about the framework.

To convert your app, replace `import bevyframe` with `import bevy2flask` only in the script contains `Frame` object and it will be ready.
You don't need to do anything to any other file including pages.

> [!WARNING]
> If you use config file instead of a main script, you must create a main script. You can look for an example from BevyFrame repository's tests folder. 