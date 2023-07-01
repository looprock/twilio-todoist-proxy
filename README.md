# twilio-todoist-proxy
Accept twilio webhooks to submit to todoist API.

# But why?
I created this project pretty much exclusively to be able to send todo items from my Apple watch. I can use Siri to say something like "Text todoist" with twilio as the contact number. Siri handles the speech to text portion and sends the message to twilio, which is configured to point SMS at this proxy, which then creates a new task in todoist. It's pretty Rube Goldberg. Is it a bit gratuitous? Absolutely, but also very handy as I often find myself in my *default mode* while driving and think of things I need to do. Is there an easier way to go about this?  Probably, but when you have an API hammer everything becomes an API nail.

# Configuration
Copy twilio-todoist-proxy.toml.example to twilio-todoist-proxy.toml, then edit it.

To use the docker image available at https://github.com/looprock/twilio-todoist-proxy/pkgs/container/twilio-todoist-proxy  mount twilio-todoist-proxy.toml to /etc/twilio-todoist-proxy.toml in your container.

__token__: your todoist API token

__project__: the todoist project you want to send all tasks to

__allowed__: whitelist of From phone numbers/submitters (things in the 'From' parameter)

This project uses dynaconf for configuration, so you can prefix the capitalized versions of the keys in the configuration, prefixed with `TODOGW_` to override the values in the configuration file, RE: 

`TODOGW_TOKEN=foo` would override the config key 'token' with the value `foo`.

It also supports environment sub-sections of the config, merging the values with the default values. For example, if you have an allowed list of `foo,bar` in the `[default]` section and want to add a testing value of `test` you can add an entry:

```
[development]
allowed = ["test"]
```

Which will create a complete allowed list of `foo,bar,test` if you set: `ENV_FOR_DYNACONF=development`

If you then added `token = 'bass'` to the development section, that would become the new values for token, as the default would be overwritten by the development section.

See for more details: https://www.dynaconf.com/

