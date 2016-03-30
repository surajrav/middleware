<%
    def get_gid(user):
        group = ds.get_by_id('groups', user['group'])
        return group['gid'] if group else 65534

%>\
% for user in ds.query("users"):
${user['username']}:${user['unixhash']}:${user['uid']}:${get_gid(user)}::0:0:${user['full_name']}:${user['home']}:${user['shell']}
% endfor
