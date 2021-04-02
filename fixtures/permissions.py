


crud =  ['create', 'read', 'update', 'delete']

DataGroup = {}
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
    **DataGroup,
    **AccountGroup,
    **StaffGroup,
    
    'staff': crud,
    'admin': crud,
}