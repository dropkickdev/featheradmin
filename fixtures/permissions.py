

crud =  ['create', 'read', 'update', 'delete']

# Default account
AccountGroup = {
    'profile': ['read', 'update'],
    'account': ['read', 'update'],
    'message': crud,
}
ContentGroup = {
    'content': crud
}

# For attachment
StaffGroup = {
    'user': ['create', 'read', 'update', 'ban', 'unban'],
    'group': crud + ['attach', 'detach'],
    'permission': crud + ['attach', 'detach'],
    'taxonomy': crud,
}
AdminGroup = {
    **ContentGroup,
    **AccountGroup,
    **StaffGroup,
    
    'staff': crud,
    'admin': [*crud, 'settings'],
}
NoaddGroup = {
    'foo': ['read', 'update', 'delete', 'hard_delete'],
    'user': ['create', 'delete', 'hard_delete'],
}