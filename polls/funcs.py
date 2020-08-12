def voted_choice(choices, author):
    for choice in choices:
        if choice.votes.filter(id=author.id).exists():
            return choice


def birth_day_context(author):
    context = {
        'birth_day': author.birth_date.day,
        'birth_month': author.birth_date.month,
        'birth_year': author.birth_date.year,
    }
    return context


def get_comments_tree(comments):
    pre_tree = get_comments_pre_tree(comments)
    return get_comments_tree_lines(pre_tree)


def get_comments_pre_tree(comments):
    pre_tree = {}
    for comment in comments:
        if comment.rel_comment not in comments:
            if comment.comment_set.all():
                children = {}
                for child in comment.comment_set.all():
                    if child.comment_set.all():
                        children[child] = get_comments_pre_tree(child.comment_set.all())
                    else:
                        children[child] = {}
                pre_tree[comment] = children
            else:
                pre_tree[comment] = {}
    return pre_tree


def get_comments_tree_lines(comments, depth=0):
    print(comments)
    tree = []
    for comment, children in comments.items():
        tree.append((comment.comment_text, depth * 10))
        if children:
            tree.extend(get_comments_tree_lines(children, depth+1))
    print(tree)
    return tree
