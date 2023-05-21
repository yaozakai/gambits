import socket
# RECAPTCHA_PUBLIC_KEY = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
# RECAPTCHA_PRIVATE_KEY = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"
# RECAPTCHA_PUBLIC_KEY = "f75294df-820b-4c94-9dc3-61544d36eb11"
RECAPTCHA_PUBLIC_KEY = "6LdaDkMkAAAAAEb-D-f0QwpY9VecOxeKNEyUzX-_"
RECAPTCHA_PRIVATE_KEY = "6LdaDkMkAAAAADSxpkyC0xrSXRhrSceaU8GZ2F-O"
# SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:rR0sWw9GPJ14@gambits-db.cqzbnbnbi3rk.ap-northeast-2.rds.amazonaws.com:5432/postgres'

if socket.gethostname() == 'srv.gambits.vip':
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://admin_admin:uDnf3QLZkbCXHVb7@srv.gambits.vip:3306/admin_db'
elif socket.gethostname() == 'The-Only-Real-MacBook-Pro.local':
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://admin_admin:uDnf3QLZkbCXHVb7@185.221.201.253:3306/admin_db'
SQLALCHEMY_ENGINE_OPTIONS = {
    # 'pool': QueuePool(creator),
    # 'pool_size': 10,
    'pool_recycle': 40
    # 'pool_pre_ping': True
}
AWS_SECRET_ACCESS_KEY = 'SFUB68Bagx/zFFX5H6KWZx7XtQCY//asIYei+UyU'
BANK_ADDRESS = '0x6E38B4dc98854E5CA41db2F9AfaCE7F7656ab33B'
ETHERSCAN_API_KEY = 'PUXKJQAECKT16NJFHJTEB6UVYSKH7F2Z8Q'
BSNSCAN_API_KEY = '49ECAJH85URFXKPMF55CFRYYGG68EP5TTS'