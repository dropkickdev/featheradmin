


crud =  ['create', 'read', 'update', 'delete']

ContentGroup = {
    'content': crud
}
AccountGroup = {
    'profile': ['read', 'update'],
    'account': ['read', 'update'],
    'message': crud,
}
StaffGroup = {
    'user': ['create', 'read', 'update', 'ban', 'unban'],
    'group': crud,
    'permission': crud,
    'taxonomy': crud,
}
AdminGroup = {
    **ContentGroup,
    **AccountGroup,
    **StaffGroup,
    
    'staff': crud,
    'admin': [*crud, 'settings'],
}