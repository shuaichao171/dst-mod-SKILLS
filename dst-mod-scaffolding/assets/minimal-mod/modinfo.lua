name = 'Example DST Mod'
description = 'Replace this description.'
author = 'Replace this author.'
version = '0.1.0'

api_version = 10
dst_compatible = true

client_only_mod = false
all_clients_require_mod = true

configuration_options =
{
    {
        name = 'enabled',
        label = 'Enabled',
        options =
        {
            { description = 'Yes', data = true },
            { description = 'No', data = false },
        },
        default = true,
    },
}
