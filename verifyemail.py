'''
在线验证邮箱真实性
'''

import optparse
import random
import smtplib
import logging
import time

import dns.resolver

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s [line:%(lineno)d] - %(levelname)s: %(message)s')

logger = logging.getLogger()


def fetch_mx(host):
    '''
    解析服务邮箱
    :param host:
    :return:
    '''
    logger.info('正在查找邮箱服务器')
    answers = dns.resolver.query(host, 'MX')
    res = [str(rdata.exchange)[:-1] for rdata in answers]
    logger.info('查找结果为：%s' % res)
    return res


def verify_istrue(email):
    '''
    :param email:
    :return:
    '''
    email_list = []
    email_obj = {}
    final_res = {
        "alive": [], # 存活
        "dead": [],  # 销毁
        "None": []   # 未知
    }
    if isinstance(email, str) or isinstance(email, bytes):
        email_list.append(email)
    else:
        email_list = email

    for em in email_list:
        name, host = em.split('@')
        if email_obj.get(host):
            email_obj[host].append(em)
        else:
            email_obj[host] = [em]

    for key in email_obj.keys():
        host = random.choice(fetch_mx(key))
        logger.info('正在连接服务器...：%s' % host)
        s = smtplib.SMTP(host, timeout=10)
        for need_verify in email_obj[key]:
            helo = s.docmd('HELO chacuo.net')
            logger.debug(helo)

            send_from = s.docmd('MAIL FROM:<3121113@chacuo.net>')
            logger.debug(send_from)
            send_from = s.docmd('RCPT TO:<%s>' % need_verify)
            logger.debug(send_from)
            if send_from[0] == 250 or send_from[0] == 451:
                final_res["alive"].append(need_verify)  # 存在
            elif send_from[0] == 550:
                final_res["dead"].append(need_verify)  # 不存在
            else:
                final_res["None"].append(need_verify)  # 未知

        s.close()

    return final_res

def parse_options():
    opt = optparse.OptionParser()
    opt.add_option("-e", "--email", help="验证邮件地址")
    opt.add_option("-l", "--list", help="验证邮件地址列表")

    (options,args) = opt.parse_args()
    # print(options,args)
    if not (options.list or options.email):
        opt.print_help()
        exit(0)
    
    return options


if __name__ == '__main__':
    opt = parse_options()
    check_list = []
    if opt.email:
        check_list.append(opt.email)
    elif opt.list:
        with open(opt.list, "r") as f:
            for line in f.readlines():
                line = line.strip()
                if line != "":
                    check_list.append(line)

    final_list = verify_istrue(check_list)

    print("存活：")
    for k in final_list.get("alive"):
        print(k)
    
    print("不存活：")
    for k in final_list.get("dead"):
        print(k)

    print("未知：")
    for k in final_list.get("None"):
        print(k)
