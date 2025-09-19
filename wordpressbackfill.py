import mysql.connector
import openai

# openai.api_key = "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"
openai.api_key= "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"


def get_meta_description(blog_post):

    asdf = True
    while asdf:
        try:
            messages = []

            messages.append(
                {
                    "role": "system",
                    "content": "You are an elite blogger. You are part of an automated system, and you need to transform the user's blog post into a Yoast SEO meta description.",
                }
            )

            messages.append(
                {
                    "role": "user",
                    "content": blog_post,
                }
            )
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
            )
            asdf=False

        except Exception as e:
            print(e)
            blog_post = blog_post[:len(blog_post)//2]
    

    return response.choices[0].message.content.strip()


def get_all_blogs(host, user, passwd, dbname):
    """Fetch all published blog posts."""
    blogs = []
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            passwd=passwd,
            database=dbname
        )
        cursor = conn.cursor()

        select_query = """
        SELECT ID, post_title, post_content, post_date
        FROM wp_posts
        WHERE post_type = 'post' AND post_status = 'publish'
        """
        cursor.execute(select_query)

        
        for (post_id, title, content, date) in cursor:
            blogs.append({
                'post_id': post_id,
                'title': title,
                'content': content,
                'date': date
            })

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if conn:
            conn.close()
        if cursor:
            cursor.close()

    return blogs

def update_yoast_data(host, user, passwd, dbname, post_id, meta_description):
    """Update Yoast focus keyword and meta description for a specific post."""
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            passwd=passwd,
            database=dbname
        )
        cursor = conn.cursor()
        
        # check if metadata exists
        select_meta_description_query = """
        SELECT meta_value
        FROM wp_postmeta
        WHERE post_id = %s AND meta_key = '_yoast_wpseo_metadesc'
        """
        cursor.execute(select_meta_description_query, (post_id,))
        meta_description_result = cursor.fetchone()
        if meta_description_result:
            print("Meta description already exists. Skipping.")
            return
        

        # Create metadata
        insert_meta_description_query = """
        INSERT INTO wp_postmeta (post_id, meta_key, meta_value)
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_meta_description_query, (post_id, '_yoast_wpseo_metadesc', meta_description))
        
        
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if conn:
            conn.close()
        if cursor:
            cursor.close()

if __name__ == "__main__":
    HOST = "86.38.202.154"
    USER = "u848597074_m32oH"
    PASSWD = "QueryGruntPassword12!"
    DBNAME = "u848597074_Z0K0u"

    # Fetch all blog posts
    blogs = get_all_blogs(HOST, USER, PASSWD, DBNAME)
    #print(blogs[0])

    # check if there is a meta description
    # if there is, skip

    for i in blogs:
        summarized = get_meta_description(i['content'])
        # print title
        print(i['title'])

        update_yoast_data(HOST, USER, PASSWD, DBNAME, i['post_id'], summarized)